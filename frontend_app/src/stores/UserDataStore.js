import { defineStore } from "pinia";



export const useUserDataStore = defineStore('userDataStore', {
    state: () => ({
        userAuthenticated: false,
        userProfileData: {}
    }),
    persist: {
        enabled: true,
        strategies: [
          {
            key: 'test-store',
          },
        ],
      }
})