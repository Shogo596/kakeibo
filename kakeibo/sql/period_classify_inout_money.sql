/*
 * 【収入支出期間分類データ抽出クエリ】
 * パラメータの範囲で指定した期間の年月ごと分類ごとの合計収入支出金額を抽出する。
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

-- 期間分類集計の一時テーブルを作成する。
call create_temp_period_classify_total(@ym_start, @ym_end, @in_out_kubun, @kotei_hendo_kubun);

-- 収入支出分類で集計する。
select
	対象年月,
	収入支出分類コード,
	収入支出分類名,
	sum(合計金額) as 合計金額
from 期間分類集計
group by
	対象年月,
	収入支出分類コード
order by
	cast(収入支出分類表示順序 as SIGNED),
	cast(対象年月 as SIGNED)
;
