class MessageListView(APIView):
    authentication_classes = [CompanyAPIKeyAuthentication]
    permission_classes = [IsAuthenticated]
    openai.api_key = "sk-proj-MCElNi8zbS3vZeIKKMEsadadsZjhiPxb50ttOiNCwsmA5yZ74zKghCb9hO0B-YkUn79JMT3BlbkFJ7ZOK-caESNohudPrBDaVvIp5ymbSR3gK9k6v2LBRJNhFxMpb0RSsaxJ0mQqhwrdht7pLYeLNMA"

    def get(self, request):
        # Get today's date
        today = now().replace(hour=0, minute=0, second=0, microsecond=0)

        # Get sender and number from query parameters
        msg_sender = request.query_params.get('msg_sender')
        msg_sender_number = request.query_params.get('msg_sender_number')

        if not msg_sender or not msg_sender_number:
            return Response({"error": "msg_sender and msg_sender_number are required."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Get the company associated with the request
        company = request.company

        # Get welcome message and admin image
        welcome_message = company.welcome_message or "به پشتیبانی خوش آمدید!"
        adminImg = request.user.image.url

        # Separate messages by received=True and received=False
        received_true_messages = Meesages.objects.filter(
            Q(create__gte=today) &
            Q(received=True) &
            Q(company=company) &  # Filter by company
            (
                    (Q(msg_sender=msg_sender) & Q(msg_sender_number=msg_sender_number) & Q(
                        msg_receiver=request.user.name)) |
                    (Q(msg_sender=request.user.name) & Q(msg_receiver=msg_sender) & Q(
                        msg_receiver_number=msg_sender_number))
            )
        ).order_by('create')

        received_false_messages = Meesages.objects.filter(
            Q(create__gte=today) &
            Q(received=False) &
            Q(company=company) &  # Filter by company
            (
                    (Q(msg_sender=msg_sender) & Q(msg_sender_number=msg_sender_number) & Q(
                        msg_receiver=request.user.name)) |
                    (Q(msg_sender=request.user.name) & Q(msg_receiver=msg_sender) & Q(
                        msg_receiver_number=msg_sender_number))
            )
        ).order_by('create')

        # Serialize messages with tags
        def serialize_messages(messages):
            messages_data = []
            for message in messages:
                tag = "received" if message.msg_sender == request.user.name else "sent"
                message_data = MessageSerializer(message).data
                message_data["id"] = message.id
                message_data["tag"] = tag
                message_data["msgImg"] = message.msgImg
                message_data["create"] = message.create
                message_data["msgFile"] = message.msgFile.url if message.msgFile else None
                message_data["company"] = message.company.name if message.company else None
                messages_data.append(message_data)
            return messages_data

        received_true_serialized = serialize_messages(received_true_messages)
        received_false_serialized = serialize_messages(received_false_messages)

        return Response({
            "welcome": welcome_message,
            "admin_img": adminImg,
            "received_true_messages": received_true_serialized,
            "received_false_messages": received_false_serialized,
            "admin": request.company.name
        }, status=status.HTTP_200_OK)

    def patch(self, request, message_id):
        try:
            message = Meesages.objects.get(id=message_id)
            message.received = True
            message.save()
            return Response({"message": "Message marked as received successfully."}, status=200)
        except Meesages.DoesNotExist:
            return Response({"error": "Message not found."}, status=404)

    def post(self, request):
        # print(request.data)
        data = request.data.copy()
        # دریافت فیلدهای مربوط به فایل (در صورت ارسال)
        file_base64 = data.pop('msgFile_base64', None)
        file_name = data.pop('file_name', None)

        serializer = MessageSerializer(data=request.data)
        if serializer.is_valid():
            message = serializer.save(msg_receiver=request.user.name, msg_receiver_number='', msgImg='',
                                      company=request.company, received=False, processed_by_api=False, msgFile='')

            if file_base64 and file_name:
                try:
                    decoded_file = base64.b64decode(file_base64)
                    message.msgFile.save(file_name, ContentFile(decoded_file))
                except Exception as e:
                    return Response({"error": f"Failed to process file: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

            connection = Connection.objects.filter(userEmail=message.msg_sender, userNumber=message.msg_sender_number,
                                                   company=request.company).exists()
            if connection:
                Connection.objects.filter(userEmail=message.msg_sender, userNumber=message.msg_sender_number,
                                          company=request.company).delete()
                Connection.objects.create(userEmail=message.msg_sender, userNumber=message.msg_sender_number,
                                          admin=request.user.name, company=request.company)
            else:
                Connection.objects.create(userEmail=message.msg_sender, userNumber=message.msg_sender_number,
                                          admin=request.user.name, company=request.company)

            if message.msgFile:
                try:
                    file_data = message.msgFile.read()
                    encoded_file_data = base64.b64encode(file_data).decode('utf-8')
                    # در صورت نیاز، اشاره‌گر فایل را به ابتدای فایل برگردانید
                    message.msgFile.seek(0)
                except Exception as e:
                    encoded_file_data = None
            else:
                encoded_file_data = None

            file_name_saved = message.msgFile.name if message.msgFile else None

            process_message.delay(
                message.id,
                file_data=encoded_file_data,
                file_name=file_name_saved
            )
            try:
                subscription = request.user.subscription
                if subscription and subscription.is_active():
                    subscription.message_sent += 1
                    subscription.save()
            except UserSubscription.DoesNotExist:
                pass

            return Response({
                "id": message.id,
                "text": message.text,
                "msg_sender": message.msg_sender,
                "msg_receiver": message.msg_receiver,
                "msg_receiver_number": message.msg_receiver_number,
                "received": message.received,
                "processed_by_api": message.processed_by_api,
                "create": message.create,
                "msgImg": message.msgImg,
                "company": message.company.name if message.company else None,
                "msgFile": message.msgFile.url if message.msgFile else None
            }, status=status.HTTP_201_CREATED)

        return Response(
            {"error": "Validation failed", "details": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )

