/*
 * 【棒グラフ・折れ線グラフ表示用Javascript】
 * Template側に「<canvas id="BarAndLineChart"></canvas>」を埋め込んで、このJSを読み込む。
 * 変数値はviewsから送ること。
 */

//Template側で以下のように変数の宣言が必要。
//全体的な表示設定
//var strTitle = '期間集計';
//var arrLabels = ['2018/01/01', '2018/01/02', '2018/01/03', '2018/01/04', '2018/01/05', '2018/01/06', '2018/01/07'];
//棒グラフのY軸設定
//var numBarMax = 200;
//var numBarMin = 0;
//var numBarStepSize = 5;
//折れ線グラフのY軸設定
//var numLineMax = 15000;
//var numLineMin = 0;
//var numLineStepSize = 1000;
//収入の棒グラフ設定
//var strBar1Name = '棒グラフA';
//var arrBar1Data = [32, 13, 20, 5, 50, 25, 40];
//支出の棒グラフ設定
//var strBar1Name = '棒グラフB';
//var arrBar1Data = [22, 23, 10, 15, 40, 35, 30];
//収支差額の折れ線グラフ設定
//var strLine1Name = '折れ線A';
//var arrLine1Data = [10000, 11000, 15000, 12000, 9000, 12000, 13000];

var ctx = document.getElementById('BarAndLineChart').getContext('2d');
var myChart = new Chart(ctx, {
    type: 'bar',
    data: {
        labels: arrLabels,
        datasets: [
            {
                label: strBar1Name,
                data: arrBar1Data,
                borderColor : "rgb(54, 164, 235)",
                backgroundColor : "rgba(54, 164, 235, 0.5)",
                yAxisID: "y-axis-1",
            },
            {
                label: strBar2Name,
                data: arrBar2Data,
                borderColor: "rgb(254, 97, 132)",
                backgroundColor: "rgba(254, 97, 132, 0.5)",
                yAxisID: "y-axis-1",
            },
            {
                label: strLine1Name,
                type: "line",
                fill: false,
                data: arrLine1Data,
                borderColor: "rgb(154, 162, 235)",
                yAxisID: "y-axis-2",
            },
        ]
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
        //Y軸の値とグリッド線の制御
        scales: {
            yAxes: [
                {
                    id: "y-axis-1",
                    type: "linear",
                    position: "left",
                    ticks: {
                        max: numBarMax,
                        min: numBarMin,
                        stepSize: numBarStepSize,
                    },
                },
                {
                    id: "y-axis-2",
                    type: "linear",
                    position: "right",
                    ticks: {
                        max: numLineMax,
                        min: numLineMin,
                        stepSize: numLineStepSize,
                    },
                    //グリッド線を消す
                    gridLines: {
                        drawOnChartArea: false,
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
