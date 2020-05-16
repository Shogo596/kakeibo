/*
 * 【折れ線グラフ表示用Javascript】
 * Template側に「<canvas id="LineChart"></canvas>」を埋め込んで、このJSを読み込む。
 * 変数値はviewsから送ること。
 */

//Template側で以下のように変数の宣言が必要。
//全体的な表示設定
//var strTitle = '分類期間収支データ';
//var arrLabels = ['2018/01/01', '2018/01/02', '2018/01/03', '2018/01/04', '2018/01/05', '2018/01/06', '2018/01/07'];
//折れ線グラフのY軸設定
//var numLineMax = 15000;
//var numLineMin = 0;
//var numLineStepSize = 1000;
//折れ線グラフのデータ設定
//var strLine1Name = ['折れ線A', '折れ線B'];
//var arrLine1Data = [[10000, 11000, 15000, 12000, 9000, 12000, 13000], [11000, 10000, 16000, 11000, 10000, 11000, 14000]];

//折れ線グラフを複数表示するために動的にデータを作成する。
var arrDatasets = [];
for (var i=0; i<arrLineDatasets.length; i++){
    arrDatasets.push({
        label: arrLineNames[i],
        fill: false,
        data: arrLineDatasets[i],
        hidden: true,   //初期非表示
    });
}

var ctx = document.getElementById('LineChart').getContext('2d');
var myChart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: arrLabels,
        datasets: arrDatasets
    },
    options: {
        title: {
            display: true,
            text: strTitle,
        },
        //マウスがポイントの近くに来るとツールチップを表示できるようにする。
        tooltips: {
            mode: 'nearest',
            intersect: false,
        },
        responsive: true,
        //Y軸の制御
        scales: {
            yAxes: [
                {
                    type: "linear",
                    ticks: {
                        max: numLineMax,
                        min: numLineMin,
                        stepSize: numLineStepSize,
                    },
                },
            ],
        },
        plugins: {
            labels: {
                render: 'value',
            },
        },
    },
});
