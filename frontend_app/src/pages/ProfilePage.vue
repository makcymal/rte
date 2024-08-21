<template>
    <MenuHeader></MenuHeader>
    <div class="card shadow m-auto" style="max-width: 30vw;">
    <h2 class="h2 mb-3 fw-normal text-center">User Profile</h2>
    <template v-for="(field, index) in Object.keys(userProfileData)" v-bind:key="index">
        <h5 class="h5 mb-3 fw-normal text-center">{{ field + ":" }} {{ userProfileData[field] }}</h5>
    </template>
    </div>
</template>

<script>
import MenuHeader from '@/components/MenuHeader.vue'
import {useUserDataStore} from "@/stores/UserDataStore"
import { mapStores, mapState} from "pinia";

export default {
    name: "ProfilePage",
    components: {
    MenuHeader
  },
  computed: {
    ...mapStores(useUserDataStore),
    ...mapState(useUserDataStore, ['userProfileData']),
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