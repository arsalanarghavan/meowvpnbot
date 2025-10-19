<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;

class CardAccountController extends Controller
{
    private $dbPath;

    public function __construct()
    {
        $this->dbPath = base_path('../vpn_bot.db');
    }

    /**
     * نمایش لیست کارت‌های بانکی
     */
    public function index()
    {
        if (!file_exists($this->dbPath)) {
            return redirect()->back()->with('error', 'دیتابیس ربات یافت نشد!');
        }

        $pdo = new \PDO("sqlite:{$this->dbPath}");
        
        $cards = $pdo->query("SELECT * FROM card_accounts ORDER BY priority ASC, id DESC")->fetchAll(\PDO::FETCH_ASSOC);
        
        // آمار
        $stats = [
            'total' => count($cards),
            'active' => array_reduce($cards, function($carry, $card) {
                return $carry + ($card['is_active'] ? 1 : 0);
            }, 0),
        ];
        
        return view('card-accounts.index', compact('cards', 'stats'));
    }

    /**
     * نمایش فرم ایجاد کارت بانکی
     */
    public function create()
    {
        return view('card-accounts.create');
    }

    /**
     * ذخیره کارت بانکی جدید
     */
    public function store(Request $request)
    {
        $request->validate([
            'card_number' => 'required|digits:16',
            'card_holder' => 'required|max:100',
            'daily_limit' => 'required|integer|min:0',
            'priority' => 'required|integer|min:0',
            'note' => 'nullable|max:200',
        ]);

        if (!file_exists($this->dbPath)) {
            return redirect()->back()->with('error', 'دیتابیس ربات یافت نشد!');
        }

        try {
            $pdo = new \PDO("sqlite:{$this->dbPath}");
            
            // بررسی تکراری نبودن شماره کارت
            $stmt = $pdo->prepare("SELECT COUNT(*) FROM card_accounts WHERE card_number = :card_number");
            $stmt->execute(['card_number' => $request->card_number]);
            if ($stmt->fetchColumn() > 0) {
                return redirect()->back()->with('error', 'این شماره کارت قبلاً ثبت شده است!');
            }
            
            $stmt = $pdo->prepare("
                INSERT INTO card_accounts (card_number, card_holder, daily_limit, priority, is_active, note, current_amount, created_at)
                VALUES (:card_number, :card_holder, :daily_limit, :priority, 1, :note, 0, datetime('now'))
            ");
            
            $stmt->execute([
                'card_number' => $request->card_number,
                'card_holder' => $request->card_holder,
                'daily_limit' => $request->daily_limit,
                'priority' => $request->priority,
                'note' => $request->note,
            ]);
            
            return redirect()->route('card-accounts.index')->with('success', 'کارت بانکی با موفقیت ایجاد شد!');
            
        } catch (\Exception $e) {
            return redirect()->back()->with('error', $e->getMessage());
        }
    }

    /**
     * نمایش فرم ویرایش کارت بانکی
     */
    public function edit($id)
    {
        if (!file_exists($this->dbPath)) {
            return redirect()->back()->with('error', 'دیتابیس ربات یافت نشد!');
        }

        $pdo = new \PDO("sqlite:{$this->dbPath}");
        
        $stmt = $pdo->prepare("SELECT * FROM card_accounts WHERE id = :id");
        $stmt->execute(['id' => $id]);
        $card = $stmt->fetch(\PDO::FETCH_ASSOC);
        
        if (!$card) {
            return redirect()->back()->with('error', 'کارت بانکی یافت نشد!');
        }
        
        return view('card-accounts.edit', compact('card'));
    }

    /**
     * ویرایش کارت بانکی
     */
    public function update(Request $request, $id)
    {
        $request->validate([
            'card_number' => 'required|digits:16',
            'card_holder' => 'required|max:100',
            'daily_limit' => 'required|integer|min:0',
            'priority' => 'required|integer|min:0',
            'note' => 'nullable|max:200',
        ]);

        if (!file_exists($this->dbPath)) {
            return redirect()->back()->with('error', 'دیتابیس ربات یافت نشد!');
        }

        try {
            $pdo = new \PDO("sqlite:{$this->dbPath}");
            
            // بررسی تکراری نبودن شماره کارت (به جز همین کارت)
            $stmt = $pdo->prepare("SELECT COUNT(*) FROM card_accounts WHERE card_number = :card_number AND id != :id");
            $stmt->execute(['card_number' => $request->card_number, 'id' => $id]);
            if ($stmt->fetchColumn() > 0) {
                return redirect()->back()->with('error', 'این شماره کارت قبلاً ثبت شده است!');
            }
            
            $stmt = $pdo->prepare("
                UPDATE card_accounts 
                SET card_number = :card_number,
                    card_holder = :card_holder,
                    daily_limit = :daily_limit,
                    priority = :priority,
                    note = :note
                WHERE id = :id
            ");
            
            $stmt->execute([
                'card_number' => $request->card_number,
                'card_holder' => $request->card_holder,
                'daily_limit' => $request->daily_limit,
                'priority' => $request->priority,
                'note' => $request->note,
                'id' => $id,
            ]);
            
            return redirect()->route('card-accounts.index')->with('success', 'کارت بانکی با موفقیت ویرایش شد!');
            
        } catch (\Exception $e) {
            return redirect()->back()->with('error', $e->getMessage());
        }
    }

    /**
     * تغییر وضعیت کارت
     */
    public function toggleStatus($id)
    {
        if (!file_exists($this->dbPath)) {
            return response()->json(['success' => false, 'message' => 'دیتابیس یافت نشد!']);
        }

        try {
            $pdo = new \PDO("sqlite:{$this->dbPath}");
            
            $stmt = $pdo->prepare("
                UPDATE card_accounts 
                SET is_active = CASE WHEN is_active = 1 THEN 0 ELSE 1 END 
                WHERE id = :id
            ");
            $stmt->execute(['id' => $id]);
            
            return response()->json(['success' => true, 'message' => 'وضعیت کارت تغییر کرد!']);
            
        } catch (\Exception $e) {
            return response()->json(['success' => false, 'message' => $e->getMessage()]);
        }
    }

    /**
     * ریست کردن مبلغ روزانه
     */
    public function resetDailyAmount($id)
    {
        if (!file_exists($this->dbPath)) {
            return response()->json(['success' => false, 'message' => 'دیتابیس یافت نشد!']);
        }

        try {
            $pdo = new \PDO("sqlite:{$this->dbPath}");
            
            $stmt = $pdo->prepare("
                UPDATE card_accounts 
                SET current_amount = 0, last_reset_date = datetime('now')
                WHERE id = :id
            ");
            $stmt->execute(['id' => $id]);
            
            return response()->json(['success' => true, 'message' => 'مبلغ روزانه ریست شد!']);
            
        } catch (\Exception $e) {
            return response()->json(['success' => false, 'message' => $e->getMessage()]);
        }
    }

    /**
     * حذف کارت بانکی
     */
    public function destroy($id)
    {
        if (!file_exists($this->dbPath)) {
            return response()->json(['success' => false, 'message' => 'دیتابیس یافت نشد!']);
        }

        try {
            $pdo = new \PDO("sqlite:{$this->dbPath}");
            
            $stmt = $pdo->prepare("DELETE FROM card_accounts WHERE id = :id");
            $stmt->execute(['id' => $id]);
            
            return response()->json(['success' => true, 'message' => 'کارت بانکی با موفقیت حذف شد!']);
            
        } catch (\Exception $e) {
            return response()->json(['success' => false, 'message' => $e->getMessage()]);
        }
    }
}

