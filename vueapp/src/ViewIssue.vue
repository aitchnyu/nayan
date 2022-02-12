<template>
  <div>
    <div style="height: 75vh; width: 100%">
      <l-map :zoom.sync="zoom" :center="center" ref="map">
        <l-tile-layer url='https://api.mapbox.com/styles/v1/mapbox/streets-v11/tiles/{z}/{x}/{y}?access_token=pk.eyJ1IjoiamVzdmluIiwiYSI6ImNqeDV5emdpeTA2MHI0OG50c2N4OTZhd28ifQ.aehvE-ZEvTy-Yd0yMTSnWw'
                      attribution='&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
                      :options="{tileSize: 512, zoomOffset: -1}"/>
        <l-marker :icon="icon" :lat-lng="center">
          <l-tooltip :options="{permanent: true, interactive: true}">
            {{ title }}
          </l-tooltip>
        </l-marker>
      </l-map>
    </div>
  </div>
</template>

<script>
import L from 'leaflet'
import CircleIcon from './assets/circle.png'
import { LMap, LTileLayer, LMarker, LTooltip } from 'vue2-leaflet'
import 'leaflet/dist/leaflet.css'

const icon = L.icon({
  iconUrl: CircleIcon,
  iconSize: [8, 8], // size of the icon
  iconAnchor: [4, 4] // point of the icon which will correspond to marker's location
})

export default {
  name: 'ViewIssue',
  components: {
    LMap,
    LTileLayer,
    LMarker,
    LTooltip
  },
  props: {
    title: { type: String, required: true },
    lat: { type: Number, required: true },
    lng: { type: Number, required: true }
  },
  methods: {
    leafletCenter () {
      return this.$refs.map.mapObject.getCenter()
    }
  },
  data () {
    return {
      icon: icon,
      stateBoundary: [],
      center: { lat: this.lat, lng: this.lng },
      zoom: 15
    }
  }
}
</script>
