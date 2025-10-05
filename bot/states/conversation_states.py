from telegram.ext import ConversationHandler

# Defining conversation states as a range of integers
(
    # States for Payment
    AWAITING_AMOUNT,
    AWAITING_RECEIPT,

    # States for Purchase Flow
    SELECTING_CATEGORY,
    SELECTING_PLAN,
    CONFIRMING_PURCHASE,
    SELECTING_PAYMENT_METHOD,

    # States for Gift Card (Customer)
    AWAITING_GIFT_CODE,

    # States for Gift Card Creation (Admin)
    AWAITING_GIFT_AMOUNT,
    AWAITING_GIFT_COUNT,

    # State for User Management (Admin)
    AWAITING_USER_ID_FOR_SEARCH,

    # State for Admin adding balance to user
    AWAITING_AMOUNT_TO_ADD,

    # State for user changing a service note
    AWAITING_SERVICE_NOTE,

    # State for service renewal
    AWAITING_RENEWAL_CONFIRMATION,

    # ---> وضعیت‌های جدید <---
    # States for Admin Broadcast
    AWAITING_BROADCAST_MESSAGE,
    CONFIRMING_BROADCAST,

) = range(15)

# A constant to end the conversation from anywhere
END_CONVERSION = ConversationHandler.END