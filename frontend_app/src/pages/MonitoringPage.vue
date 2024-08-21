<template>
    <MenuHeader></MenuHeader>
    <div class="d-flex flex-column" style="align-items: center;">
      <div class="p-2">
         <button type="button" class="rounded-pill btn btn-light" @click="showBatches" id="hlit" :style="{backgroundColor: btnInactiveColor}">hlit</button>
      </div>
      <div class="p-2">
         <div class="btn-group btn-group-toggle">
         <template v-if="batchesVisible">
            <ul class="nav nav-pills mb-3" role="tablist">
            <li class="nav-item" role="presentation" v-for="(btnBatchName, btnIndex) in serverBatchesList" v-bind:key="btnIndex">
               <button class=" rounded-pill btn btn-light" data-bs-toggle="pill" type="button" role="tab" aria-selected="false" @click="renderData(btnBatchName)">{{ btnBatchName }}</button>
            </li>
            </ul>
         </template>
         </div>
      </div>
      <div class="p-2" v-if="renderVisible">
         <div class="d-flex flex-row card shadow-sm">
               <div class="d-flex flex-column justify-content-center align-items-center">
               <button class="btn" type="button" role="tab"  @click="changeRender('chart')">Chart</button>
               <div class="rounded-pill" :style="{width: '1vw', height: '0.5vh', backgroundColor: chartBtnColor}"></div>
               </div>
               <div class="d-flex flex-column flex-column justify-content-center align-items-center">
               <button class="btn" type="button" role="tab" @click="changeRender('table')">Table</button>

               <div class="rounded-pill" :style="{width: '1vw', height: '0.5vh', backgroundColor: tableBtnColor}"></div>
               </div>
      </div>
   </div>
      <div class="p-2">
        <MonitorTable v-if="renderVisible && renderType === 'table'" :server-msg="serverMsgStd" :server-table-header="serverTableHeaderStd" :avg-total-data="avgTotalData" :ext-data-on-name="true"></MonitorTable>
      </div>
      <div class="p-2 row">
      <div class="col" v-for="(clusterLabel, clindex) in serverTableHeaderStd['clustered_fields']" v-bind:key="clindex">
        <MonitorChart v-if="renderVisible && renderType === 'chart'" :cluster-label="clusterLabel" :server-data="serverMsgStd" 
        :server-fields-data-type="serverTableHeaderStd['fields_data_type']" :server-fields="Object.keys(serverTableHeaderStd['original_data'][clusterLabel])"></MonitorChart>
      </div>
   </div>
    </div>
</template>

<script>
import MenuHeader from '@/components/MenuHeader.vue'
import MonitorTable from '@/components/MonitorTable.vue'
import MonitorChart from '@/components/MonitorChart.vue'
import {useMonitoringDataStore} from "@/stores/MonitoringDataStore"
import { mapActions, mapStores, mapState, mapWritableState } from "pinia";

export default {
    name: "MonitoringPage",
    components: {
    MenuHeader,
    MonitorTable,
    MonitorChart
  },
  data() {
      return {
      batchesVisible: false,
      renderVisible: false,
      btnActiveColor: '#2F70AF',
      btnInactiveColor: '#e7d5f9',
      renderType: "chart",
      chartBtnColor: 'blue',
      tableBtnColor: 'white'
      }
   },
   computed: {
      ...mapActions(useMonitoringDataStore, ['sendMessage']),
      ...mapStores(useMonitoringDataStore),
      ...mapWritableState(useMonitoringDataStore, ['currBatch', 'currLabel']),
      ...mapState(useMonitoringDataStore, ['serverTableHeaderStd', 'serverMsgStd', 'avgTotalData', 'serverBatchesList']),
   },
   methods: {
      showBatches() {
         if (!this.batchesVisible){
            this.sendMessage('lsob');
            this.batchesVisible = true
         }
      },
      renderData (batchName){
         this.sendMessage('head?' + batchName)
         this.sendMessage('mstd?' + batchName)
         this.renderVisible = true
         this.currBatch = batchName
      },
      changeRender (type){
         if (type === 'chart'){
            this.chartBtnColor = 'blue'
            this.tableBtnColor = 'white'
         } else if (type === 'table') {
            this.tableBtnColor = 'blue'
            this.chartBtnColor = 'white'
         }
         this.renderType = type
      },

   }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
label, #slider {
  display: inline-block;
  font-weight: bold;
  text-align: center;
  background: purple;
  color: #AAA;
  width: 150px;
  height: auto;
  padding: 20px 0px;
}

label:hover {
  color: white;
  cursor: pointer;
}

#slider {
  background-color: transparent;
  position: absolute;
  border-bottom: 3px solid white;
  margin: 7px 10px;
  transition: transform 0.5s;
  width: 130px;
}

[type=radio],#r1:checked ~ #slider {
  transform: translate(-450px, 0px);
}

[type=radio],#r2:checked ~ #slider {
  transform: translate(-300px, 0px);
}
</style>