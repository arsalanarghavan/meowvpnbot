from telegram.ext import ConversationHandler

# Defining conversation states as a range of integers
(
    # States for Payment
    AWAITING_RECEIPT,
    
    # States for Purchase Flow
    SELECTING_CATEGORY,
    SELECTING_PLAN,
    CONFIRMING_PURCHASE,
    
    # States for Gift Card (Customer)
    AWAITING_GIFT_CODE,

    # States for Gift Card Creation (Admin)
    AWAITING_GIFT_AMOUNT,
    AWAITING_GIFT_COUNT,
    
    # State for User Management (Admin)
    AWAITING_USER_ID_FOR_SEARCH,

    # ---> وضعیت جدید <---
    # State for Admin adding balance to user
    AWAITING_AMOUNT_TO_ADD,

) = range(9)

# A constant to end the conversation from anywhere
END_CONVERSATION = ConversationHandler.END