/*
 * 【円グラフ表示用Javascript】
 * Template側に「<canvas id="PieChart"></canvas>」を埋め込んで、このJSを読み込む。
 * 変数値はviewsから送ること。
 */

//Template側で以下のように変数の宣言が必要。
//var strTitle = 'タイトル';
//var arrLabels = ['A型', 'O型', 'B型', 'AB型'];
//var arrData = [38, 31, 21, 10]

var ctx = document.getElementById("PieChart");
var PieChart = new Chart(ctx, {
    type: 'pie',
    data: {
        labels: arrLabels,
        datasets: [{
            data: arrData
        }]
    },
    options: {
        title: {
            display: true,
            text: strTitle
        },
        plugins: {
            colorschemes: {
                //scheme: 'brewer.Paired12'
                scheme: 'tableau.Tableau20'
            },
            labels: {
                //設定例は「https://github.com/emn178/chartjs-plugin-labels」参照。
                render: 'label',
                position: 'outside',
                //arc: true,
                outsidePadding: 4,
            },
        },
    }
});
