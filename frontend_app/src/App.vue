<template>
  <router-view/>
</template>

<script>
import axios from 'axios'
import {useUserDataStore} from "@/stores/UserDataStore"
import {useMonitoringDataStore} from "@/stores/MonitoringDataStore"
import { mapWritableState, mapStores, mapState, mapActions } from "pinia";
import router from './router';


export default {
  name: 'App',
  computed: {
    ...mapStores(useUserDataStore),
    ...mapActions(useMonitoringDataStore, ['setSocket', 'listenMsg']),
    ...mapState(useUserDataStore, ['userAuthenticated']),
    ...mapWritableState(useUserDataStore, ['userAuthenticated', 'userProfileData']),
  },
  mounted() {
    axios.get(axios.defaults.baseURL + "check-cookie-login", { withCredentials: true })
    .then((response) => {
            if(response.data.status === "OK"){
              this.userAuthenticated = true
              this.userProfileData = response.data.data
              this.setSocket;
              this.listenMsg;
              
            } else{
              this.userAuthenticated = false
            }
          }).catch(error => {
              console.log(error)
              router.push("login")
            })
  }
}
</script>

<style>

</style>
