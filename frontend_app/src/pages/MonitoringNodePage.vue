<template>
    <MenuHeader></MenuHeader>
    <div class="card shadow m-auto" style="width: 25vw;">
    <button class="btn btn-light text-center" @click="showSpec"><h2>«{{ this.currLabel }}» node specs</h2></button>
    <template v-if="specVisible">
    <div class="card shadow m-auto" style="width: 25vw;">
          <h4 class="h4 mb-3 fw-normal text-center">INFO</h4>

          <h6 class="h6 mb-3 fw-normal text-center">batch name: {{ this.currBatch }}</h6>
          <h6 class="h6 mb-3 fw-normal text-center">node name: {{ this.currLabel }}</h6>
        </div>
    <template v-for="(field, index) in Object.keys(serverMsgSpc)" v-bind:key="index">
        <div class="card shadow m-auto" style="width: 25vw;" v-if="field !== 'header'">
          <h4 class="h4 mb-3 fw-normal text-center">{{ field.toUpperCase() }}</h4>
          <template v-for="(field1, index1) in Object.keys(serverMsgSpc[field])" v-bind:key="index1">
            <h6 class="h6 mb-3 fw-normal text-center">{{ field1 + ":" }} {{ serverMsgSpc[field][field1] }}</h6>
          </template>
        </div>
    </template>
  </template>
    </div>
    <div class="d-flex flex-column" style="align-items: center;" v-if="Object.keys(serverMsgExt).length > 0">
      <div class="p2" v-for="(key, index) in Object.keys(serverTableHeaderExt)" v-bind:key="index" style="margin: 10px;">
        <MonitorTable :server-msg="serverMsgExt[key]" :server-table-header="formatHeader(serverTableHeaderExt[key], key)" :ext-data-on-name="false" ></MonitorTable>
      </div>
    </div>
    <div class="container text-center" v-else><h2>Waiting sensor response...</h2></div>
</template>

<script>
import MenuHeader from '@/components/MenuHeader.vue'
import MonitorTable from '@/components/MonitorTable.vue'
import { useMonitoringDataStore } from "@/stores/MonitoringDataStore"
import { mapActions, mapStores, mapState } from "pinia";

export default {
    name: "MonitoringNodePage",
    components: {
    MenuHeader,
    MonitorTable
  },
  data() {
    return {
      specVisible: true
    }
  },
   computed: {
      ...mapActions(useMonitoringDataStore, ['sendMessage']),
      ...mapStores(useMonitoringDataStore),
      ...mapState(useMonitoringDataStore, ['serverTableHeaderExt', 'serverMsgExt', 'serverMsgSpc', 'currBatch', 'currLabel']),
   },
   created() {
    this.sendMessage('spec?' + this.currBatch + '?' + this.currLabel)
    this.sendMessage('desc?' + this.currBatch + '?' + this.currLabel)
    this.sendMessage('mext?' + this.currBatch + '?' + this.currLabel)
  },
   methods: {
      formatHeader (headerData, key){
        let formattedData = {} // new header data formatted to fill the table

        formattedData['clustered_fields'] = [key]
        formattedData['clustered_fields_span'] = [Object.keys(headerData).length]
        formattedData['fields'] = Object.keys(headerData);
        formattedData['fields_data_type'] = headerData;
        return formattedData
      }, 
      showSpec (){
        this.specVisible = !this.specVisible
   }
  }

}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>