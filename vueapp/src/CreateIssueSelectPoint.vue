<template>
  <div>
    <div style="height: 75vh; width: 100%;">
      <l-map
        ref="map"
        :zoom.sync="zoom"
        :center="center"
        :options="{zoomSnap: 0}"
        style="height: 75vh; width: 100%"
      >
        <l-tile-layer
          url="https://api.mapbox.com/styles/v1/mapbox/streets-v11/tiles/{z}/{x}/{y}?access_token=pk.eyJ1IjoiamVzdmluIiwiYSI6ImNqeDV5emdpeTA2MHI0OG50c2N4OTZhd28ifQ.aehvE-ZEvTy-Yd0yMTSnWw"
          attribution="&copy; <a href=&quot;http://osm.org/copyright&quot;>OpenStreetMap</a> contributors"
          :options="{tileSize: 512, zoomOffset: -1}"
        />
        <l-marker
          :icon="icon"
          :lat-lng="secondCenter"
        />
      </l-map>
        <input
          type="hidden"
          name="latitude"
          :value="secondCenter.lat"
        >
        <input
          type="hidden"
          name="longitude"
          :value="secondCenter.lng"
        >
    </div>
  </div>
</template>

<script>
import L from 'leaflet'
import { LMap, LTileLayer, LMarker } from 'vue2-leaflet'

import PlusIcon from '@/assets/plus.png'

const crosshairIcon = L.icon({
  iconUrl: PlusIcon,
  iconSize: [20, 20], // size of the icon
  iconAnchor: [10, 10] // point of the icon which will correspond to marker's location
})

export default {
  name: 'SelectPoint',
  components: {
    LMap, LTileLayer, LMarker
  },
  props: {
    center: { type: Object, required: true }
  },
  data: function () {
    return {
      icon: crosshairIcon,
      secondCenter: this.center,
      zoom: 17
    }
  },
  async mounted () {
    const map = this.$refs.map.mapObject
    const that = this
    // Center does not sync back when map moves
    map.on('move', (e) => {
      that.secondCenter = map.getCenter()
    })
  },
  methods: {
    getLeafletCenter () {
      return this.$refs.map.mapObject.getCenter()
    },
    setLeafletCenter (lat, lng) {
      this.$refs.map.mapObject.panTo({ lat: lat, lng: lng })
    }
  }
}
</script>

<style>
  @import "../node_modules/buefy/dist/buefy.css";
  @import "../node_modules/leaflet/dist/leaflet.css";
  .fullwidth {
    width: 100%;
  }
  /*From https://stackoverflow.com/a/41869915*/
  @media(max-width: 768px) {
    .almost-fullscreen {
      height: 85vh;
    }
  }
  @media not all and (max-width: 768px) {
    .almost-fullscreen {
      height: 100vh;
    }
  }
</style>
