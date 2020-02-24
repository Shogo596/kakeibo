/*
 * 【収入支出期間データ抽出クエリ】
 * パラメータの範囲で指定した期間の期間ごとの合計収入支出金額を抽出する。
 * 収入支出区分や固定変動区分の指定も可能。
 * 対象テーブルは、支出明細とカード支出明細。
 */

-- 変数宣言
set @ym_start = %s;		-- 抽出範囲の開始年月
set @ym_end = %s;			-- 抽出範囲の終了年月
set @in_out_kubun = %s;		-- 抽出対象の収入支出区分（カンマ区切りで指定可能）
set @kotei_hendo_kubun = %s;	-- 抽出対象の固定変動区分（カンマ区切りで指定可能）

-- 変数設定例
-- set @ym_start = '201701';
-- set @ym_end = '201712';
-- set @in_out_kubun = '1';
-- set @kotei_hendo_kubun = '0,1';

select
	union_expense.対象年月,
	sum(union_expense.金額) as 合計金額
from (
	select
		LEFT(sm.対象年月日, 6) as 対象年月,
		sm.金額
	from mysite.kakeibo_収入支出明細 as sm
		left outer join mysite.kakeibo_収入支出分類マスタ as sbm
			on sm.収入支出分類コード_id = sbm.収入支出分類コード
		left outer join mysite.kakeibo_対象者マスタ as tm
			on sm.対象者コード_id = tm.対象者コード
	where
		sm.対象年月日 between concat(@ym_start, '00') and concat(@ym_end, '99')
    and sm.削除フラグ = '0'
    and find_in_set(sbm.収入支出区分, @in_out_kubun)
    and find_in_set(sbm.固定変動区分, @kotei_hendo_kubun)
	union all
	select
		csm.支払月 as 対象年月,
		csm.利用金額 as 金額
	from mysite.kakeibo_カード支出明細 as csm
		left outer join mysite.kakeibo_収入支出分類マスタ as sbm
			on csm.収入支出分類コード_id = sbm.収入支出分類コード
		left outer join mysite.kakeibo_対象者マスタ as tm
			on csm.対象者コード_id = tm.対象者コード
	where
		csm.支払月 between @ym_start and @ym_end
    and find_in_set(sbm.収入支出区分, @in_out_kubun)
    and find_in_set(sbm.固定変動区分, @kotei_hendo_kubun)
	and	ifnull(csm.収入支出分類コード_id, '') <> ''
	and	ifnull(csm.対象者コード_id, '') <> ''
    and csm.削除フラグ = '0'
) as union_expense
group by
	union_expense.対象年月
order by
	cast(union_expense.対象年月 as SIGNED)
;

