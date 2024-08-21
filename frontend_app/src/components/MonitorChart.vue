<template>
   <div class="card shadow text-center chart-card">
      <h3>{{ this.clusterLabel }}, {{ this.getChartDataType() }}</h3>
      <Pie
      id="my-chart-id"
      :options="chartOptions"
      :data="chartData"
   />
   </div>
</template>
   

<script>
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js'
import { Pie } from 'vue-chartjs'
import { computeAvgTotalOutput } from '../utils/prettyMonTable'

ChartJS.register(ArcElement, Tooltip, Legend)

export default {
  name: 'MonitorChart',
  components: { Pie },
  props: ['clusterLabel', 'serverData', 'serverFields', 'serverFieldsDataType'],
  data() {
    return {
      chartOptions: {
        responsive: true
      }
    }
  },
  computed: {
   chartData () {
        return {datasets: [ { data: Object.values(this.transformData(computeAvgTotalOutput(this.serverFields, this.serverFieldsDataType, this.serverData).avg)),

         backgroundColor: ['#669900', '#ccee66', '#006699', '#3399cc', '#990066', '#cc3399',
         '#ff6600', '#ffcc00', '#bce3fa', '#cb0b0a'], } ],

         labels: Object.keys(this.transformData(computeAvgTotalOutput(this.serverFields, this.serverFieldsDataType, this.serverData).avg)) }
   }
   },
  methods: {
   transformData (inputData) {
      let keys = this.filterKeys(this.serverFields, inputData)
      let data = {}
      for (let key of keys){
         data[key] = inputData[key]
      }
      return this.sortData(data)
   },
   filterKeys (keys, data) {
      let newKeys = []
      for (let key of keys){
         if (this.serverFieldsDataType[key] != 'hz' && (typeof data[key] === "number" || typeof data[key] === "bigint")){
            newKeys.push(key)
         }
      }
      return newKeys
   },
   getChartDataType () {
      return this.serverFieldsDataType[this.serverFields[0]]
   },
   sortData (data){
      let newData = {}

      // Create items array
      let items = Object.keys(data).map(function(key) {
      return [key, data[key]];
      });

      // Sort the array based on the second element
      items.sort(function(first, second) {
      return second[1] - first[1];
      });

      for (let i = 0; i < items.length; i++){
         newData[items[i][0]] = items[i][1]
      }
         return newData
   }
  }
}
</script>
   
   
<style>
 .chart-card {
   width: 23vw; 
   padding-bottom: 2vh; 
   padding-top: 2vh;
 }
</style>