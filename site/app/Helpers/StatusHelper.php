<?php

namespace App\Helpers;

/**
 * Helper class for mapping status values between Python Enums and PHP strings.
 * 
 * This ensures consistency between the Python bot code and PHP Laravel panel.
 */
class StatusHelper
{
    /**
     * Transaction Status constants matching Python TransactionStatus enum values
     */
    const TRANSACTION_PENDING = 'در انتظار';
    const TRANSACTION_COMPLETED = 'موفق';
    const TRANSACTION_FAILED = 'ناموفق';

    /**
     * Transaction Type constants matching Python TransactionType enum values
     */
    const TRANSACTION_TYPE_WALLET_CHARGE = 'شارژ کیف پول';
    const TRANSACTION_TYPE_SERVICE_PURCHASE = 'خرید سرویس';
    const TRANSACTION_TYPE_GIFT_CARD = 'کارت هدیه';

    /**
     * Plan Category constants matching Python PlanCategory enum values
     */
    const PLAN_CATEGORY_NORMAL = 'عادی';
    const PLAN_CATEGORY_SPECIAL = 'ویژه';
    const PLAN_CATEGORY_GAMING = 'گیمینگ';
    const PLAN_CATEGORY_TRADE = 'ترید';

    /**
     * Get all valid transaction status values
     *
     * @return array
     */
    public static function getTransactionStatuses(): array
    {
        return [
            self::TRANSACTION_PENDING,
            self::TRANSACTION_COMPLETED,
            self::TRANSACTION_FAILED,
        ];
    }

    /**
     * Check if a transaction status is valid
     *
     * @param string $status
     * @return bool
     */
    public static function isValidTransactionStatus(string $status): bool
    {
        return in_array($status, self::getTransactionStatuses(), true);
    }

    /**
     * Get transaction status label (with emoji for display)
     *
     * @param string $status
     * @return string
     */
    public static function getTransactionStatusLabel(string $status): string
    {
        $labels = [
            self::TRANSACTION_PENDING => '⏳ در انتظار',
            self::TRANSACTION_COMPLETED => '✅ موفق',
            self::TRANSACTION_FAILED => '❌ ناموفق',
        ];

        return $labels[$status] ?? $status;
    }

    /**
     * Get transaction status badge variant for UI components
     *
     * @param string $status
     * @return string
     */
    public static function getTransactionStatusVariant(string $status): string
    {
        $variants = [
            self::TRANSACTION_PENDING => 'outline',
            self::TRANSACTION_COMPLETED => 'secondary',
            self::TRANSACTION_FAILED => 'destructive',
        ];

        return $variants[$status] ?? 'outline';
    }

    /**
     * Get all valid transaction type values
     *
     * @return array
     */
    public static function getTransactionTypes(): array
    {
        return [
            self::TRANSACTION_TYPE_WALLET_CHARGE,
            self::TRANSACTION_TYPE_SERVICE_PURCHASE,
            self::TRANSACTION_TYPE_GIFT_CARD,
        ];
    }

    /**
     * Get all valid plan category values
     *
     * @return array
     */
    public static function getPlanCategories(): array
    {
        return [
            self::PLAN_CATEGORY_NORMAL,
            self::PLAN_CATEGORY_SPECIAL,
            self::PLAN_CATEGORY_GAMING,
            self::PLAN_CATEGORY_TRADE,
        ];
    }

    /**
     * Check if a plan category is valid
     *
     * @param string $category
     * @return bool
     */
    public static function isValidPlanCategory(string $category): bool
    {
        return in_array($category, self::getPlanCategories(), true);
    }

    /**
     * Get plan category label (with emoji for display)
     *
     * @param string $category
     * @return string
     */
    public static function getPlanCategoryLabel(string $category): string
    {
        $labels = [
            self::PLAN_CATEGORY_NORMAL => '🌐 عادی',
            self::PLAN_CATEGORY_SPECIAL => '🚀 ویژه',
            self::PLAN_CATEGORY_GAMING => '🎮 گیمینگ',
            self::PLAN_CATEGORY_TRADE => '📈 ترید',
        ];

        return $labels[$category] ?? $category;
    }
}

