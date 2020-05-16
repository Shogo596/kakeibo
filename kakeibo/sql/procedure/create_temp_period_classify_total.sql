use mysite;

-- ストアド内で「;」を使うとそこでストアドが終わってしまうので区切り文字を「//」に変更する。最後に元に戻している。
DELIMITER //

-- ストアドをdrop, createする。
DROP PROCEDURE IF EXISTS create_temp_period_classify_total//
CREATE PROCEDURE create_temp_period_classify_total(
	IN ym_start CHAR(6),				-- 取得開始年月日
    IN ym_end CHAR(6),					-- 取得終了年月日
    IN in_out_kubun VARCHAR(5),			-- 収入支出区分
    IN kotei_hendo_kubun VARCHAR(5)		-- 固定変動区分
)
BEGIN
/*
 * 【期間分類集計TEMPテーブル作成】
 * パラメータの範囲で指定した期間の分類ごとの収入支出金額を抽出して「期間分類集計」というTEMPテーブルを作成する。
 * 収入支出区分や固定変動区分の指定も可能。
 * 対象テーブルは、支出明細とカード支出明細。
 */
	drop temporary table if exists 期間分類集計;
	create temporary table 期間分類集計 as
	select
		union_expense.対象年月,
		union_expense.収入支出分類コード,
		union_expense.収入支出分類名,
		union_expense.収入支出分類表示順序,
		union_expense.対象者コード,
		union_expense.対象者名,
		union_expense.対象者表示順序,
		sum(union_expense.金額) as 合計金額
	from (
		select
			LEFT(sm.対象年月日, 6) as 対象年月,
			sbm.収入支出分類コード ,
			sbm.収入支出分類名,
			sbm.表示順序 as 収入支出分類表示順序,
			tm.対象者コード,
			tm.対象者名,
			tm.表示順序 as 対象者表示順序,
			sm.金額
		from mysite.kakeibo_収入支出明細 as sm
			left outer join mysite.kakeibo_収入支出分類マスタ as sbm
				on sm.収入支出分類コード_id = sbm.収入支出分類コード
			left outer join mysite.kakeibo_対象者マスタ as tm
				on sm.対象者コード_id = tm.対象者コード
		where
			sm.対象年月日 between concat(ym_start, '00') and concat(ym_end, '99')
		and sm.削除フラグ = '0'
		and find_in_set(sbm.収入支出区分, in_out_kubun)
		and find_in_set(sbm.固定変動区分, kotei_hendo_kubun)
		union all
		select
			csm.支払月 as 対象年月,
			sbm.収入支出分類コード,
			sbm.収入支出分類名,
			sbm.表示順序 as 収入支出分類表示順序,
			tm.対象者コード,
			tm.対象者名,
			tm.表示順序 as 対象者表示順序,
			csm.利用金額 as 金額
		from mysite.kakeibo_カード支出明細 as csm
			left outer join mysite.kakeibo_収入支出分類マスタ as sbm
				on csm.収入支出分類コード_id = sbm.収入支出分類コード
			left outer join mysite.kakeibo_対象者マスタ as tm
				on csm.対象者コード_id = tm.対象者コード
		where
			csm.支払月 between ym_start and ym_end
		and find_in_set(sbm.収入支出区分, in_out_kubun)
		and find_in_set(sbm.固定変動区分, kotei_hendo_kubun)
		and	ifnull(csm.収入支出分類コード_id, '') <> ''
		and	ifnull(csm.対象者コード_id, '') <> ''
		and csm.削除フラグ = '0'
	) as union_expense
	group by
		union_expense.対象年月,
		union_expense.収入支出分類コード,
		union_expense.対象者コード
	order by
		cast(union_expense.対象年月 as SIGNED),
		cast(union_expense.収入支出分類表示順序 as SIGNED),
		cast(union_expense.対象者表示順序 as SIGNED)
	;
END
//
DELIMITER ;