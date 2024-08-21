<template>
    <MenuHeader></MenuHeader>
    <div class="container">
    </div>
</template>

<script>
import MenuHeader from '@/components/MenuHeader.vue'
import {useMonitoringDataStore} from "@/stores/MonitoringDataStore"
import { mapActions, mapStores, mapState, mapWritableState } from "pinia";

export default {
    name: "MainPage",
    components: {
    MenuHeader
  },
  computed: {
    ...mapActions(useMonitoringDataStore, ['sendMessage']),
    ...mapStores(useMonitoringDataStore),
    ...mapState(useMonitoringDataStore, ['socket', 'serverMsgStd']),
    ...mapWritableState(useMonitoringDataStore, ['socket']),

  },
  mounted() {

  },
  methods: {
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>