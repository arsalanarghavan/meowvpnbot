<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Str;

class GiftCardController extends Controller
{
    /**
     * نمایش لیست کارت‌های هدیه
     */
    public function index(Request $request)
    {
        if (!$this->botDatabaseExists()) {
            return redirect()->back()->with('error', 'دیتابیس ربات یافت نشد!');
        }

        $pdo = $this->getBotConnection();
        
        $status = $request->get('status');
        
        $query = "
            SELECT g.*, u.user_id
            FROM gift_cards g
            LEFT JOIN users u ON g.used_by_user_id = u.user_id
            WHERE 1=1
        ";
        $params = [];
        
        if ($status && $status != 'all') {
            $isUsed = $status == 'used' ? 1 : 0;
            $query .= " AND g.is_used = :status";
            $params['status'] = $isUsed;
        }
        
        $query .= " ORDER BY g.id DESC";
        
        $stmt = $pdo->prepare($query);
        $stmt->execute($params);
        $giftCards = $stmt->fetchAll(\PDO::FETCH_ASSOC);
        
        // آمار
        $stmt = $pdo->prepare("SELECT COUNT(*) FROM gift_cards");
        $stmt->execute();
        $stats['total'] = $stmt->fetchColumn();
        
        $stmt = $pdo->prepare("SELECT COUNT(*) FROM gift_cards WHERE is_used = 1");
        $stmt->execute();
        $stats['used'] = $stmt->fetchColumn();
        
        $stmt = $pdo->prepare("SELECT COUNT(*) FROM gift_cards WHERE is_used = 0");
        $stmt->execute();
        $stats['unused'] = $stmt->fetchColumn();
        
        $stmt = $pdo->prepare("SELECT IFNULL(SUM(amount), 0) FROM gift_cards");
        $stmt->execute();
        $stats['total_amount'] = $stmt->fetchColumn();
        
        $stmt = $pdo->prepare("SELECT IFNULL(SUM(amount), 0) FROM gift_cards WHERE is_used = 1");
        $stmt->execute();
        $stats['used_amount'] = $stmt->fetchColumn();
        
        return view('gift-cards.index', compact('giftCards', 'stats'));
    }

    /**
     * نمایش فرم ایجاد کارت هدیه
     */
    public function create()
    {
        return view('gift-cards.create');
    }

    /**
     * ذخیره کارت هدیه جدید
     */
    public function store(Request $request)
    {
        $request->validate([
            'amount' => 'required|integer|min:1000',
            'count' => 'required|integer|min:1|max:100',
        ]);

        if (!$this->botDatabaseExists()) {
            return redirect()->back()->with('error', 'دیتابیس ربات یافت نشد!');
        }

        try {
            $pdo = $this->getBotConnection();
            $pdo->beginTransaction();
            
            $count = $request->count;
            $amount = $request->amount;
            $codes = [];
            
            for ($i = 0; $i < $count; $i++) {
                // تولید کد یونیک
                do {
                    $code = $this->generateGiftCardCode();
                    $stmt = $pdo->prepare("SELECT COUNT(*) FROM gift_cards WHERE code = :code");
                    $stmt->execute(['code' => $code]);
                    $exists = $stmt->fetchColumn() > 0;
                } while ($exists);
                
                // ذخیره کارت هدیه
                $stmt = $pdo->prepare("
                    INSERT INTO gift_cards (code, amount, is_used, used_by_user_id)
                    VALUES (:code, :amount, 0, NULL)
                ");
                $stmt->execute([
                    'code' => $code,
                    'amount' => $amount,
                ]);
                
                $codes[] = $code;
            }
            
            $pdo->commit();
            
            return redirect()->route('gift-cards.index')->with([
                'success' => "{$count} کارت هدیه با موفقیت ایجاد شد!",
                'codes' => $codes
            ]);
            
        } catch (\Exception $e) {
            $pdo->rollBack();
            return redirect()->back()->with('error', $e->getMessage());
        }
    }

    /**
     * حذف کارت هدیه
     */
    public function destroy($id)
    {
        if (!$this->botDatabaseExists()) {
            return response()->json(['success' => false, 'message' => 'دیتابیس یافت نشد!']);
        }

        try {
            $pdo = $this->getBotConnection();
            
            // بررسی استفاده شده بودن
            $stmt = $pdo->prepare("SELECT is_used FROM gift_cards WHERE id = :id");
            $stmt->execute(['id' => $id]);
            $isUsed = $stmt->fetchColumn();
            
            if ($isUsed) {
                return response()->json(['success' => false, 'message' => 'کارت هدیه استفاده شده قابل حذف نیست!']);
            }
            
            $stmt = $pdo->prepare("DELETE FROM gift_cards WHERE id = :id");
            $stmt->execute(['id' => $id]);
            
            return response()->json(['success' => true, 'message' => 'کارت هدیه با موفقیت حذف شد!']);
            
        } catch (\Exception $e) {
            return response()->json(['success' => false, 'message' => $e->getMessage()]);
        }
    }

    /**
     * تولید کد کارت هدیه
     */
    private function generateGiftCardCode()
    {
        // فرمت: XXXX-XXXX-XXXX
        $part1 = strtoupper(Str::random(4));
        $part2 = strtoupper(Str::random(4));
        $part3 = strtoupper(Str::random(4));
        
        return "{$part1}-{$part2}-{$part3}";
    }

    /**
     * دریافت لیست کارت‌های هدیه به صورت JSON (API)
     */
    public function apiIndex(Request $request)
    {
        if (!$this->botDatabaseExists()) {
            return response()->json(['success' => false, 'message' => 'دیتابیس ربات یافت نشد!'], 404);
        }

        try {
            $pdo = $this->getBotConnection();
            
            $query = "
                SELECT g.*, u.user_id
                FROM gift_cards g
                LEFT JOIN users u ON g.used_by_user_id = u.user_id
                WHERE 1=1
            ";
            $params = [];
            
            if ($request->has('status')) {
                $isUsed = $request->get('status') === 'used' ? 1 : 0;
                $query .= " AND g.is_used = :status";
                $params['status'] = $isUsed;
            }
            
            $query .= " ORDER BY g.id DESC";
            
            $stmt = $pdo->prepare($query);
            $stmt->execute($params);
            $giftCards = $stmt->fetchAll(\PDO::FETCH_ASSOC);
            
            return response()->json(['success' => true, 'data' => $giftCards]);
        } catch (\Exception $e) {
            return response()->json(['success' => false, 'message' => $e->getMessage()], 500);
        }
    }

    /**
     * دریافت جزئیات کارت هدیه به صورت JSON (API)
     */
    public function apiShow($id)
    {
        if (!$this->botDatabaseExists()) {
            return response()->json(['success' => false, 'message' => 'دیتابیس ربات یافت نشد!'], 404);
        }

        try {
            $pdo = $this->getBotConnection();
            
            $stmt = $pdo->prepare("
                SELECT g.*, u.user_id
                FROM gift_cards g
                LEFT JOIN users u ON g.used_by_user_id = u.user_id
                WHERE g.id = :id
            ");
            $stmt->execute(['id' => $id]);
            $giftCard = $stmt->fetch(\PDO::FETCH_ASSOC);
            
            if (!$giftCard) {
                return response()->json(['success' => false, 'message' => 'کارت هدیه یافت نشد!'], 404);
            }
            
            return response()->json(['success' => true, 'data' => $giftCard]);
        } catch (\Exception $e) {
            return response()->json(['success' => false, 'message' => $e->getMessage()], 500);
        }
    }
}

