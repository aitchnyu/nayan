<template>
  <div>
    <link
      rel="stylesheet"
      :href="stylesheet"
    >
    <div>
      <l-map
        ref="map"
        :zoom.sync="zoom"
        :center="center"
        :options="{zoomSnap: 0}"
        style="height: 50vh; width: 100%"
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
      <portal selector="#portal-target">
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
      </portal>
    </div>
  </div>
</template>

<script>
  import axios from 'axios'
  import debounce from 'lodash/debounce'
  import { Portal } from '@linusborg/vue-simple-portal'
  import L from 'leaflet'
  import { LMap, LTileLayer, LIcon, LMarker, LPopup, LTooltip, LPolygon } from 'vue2-leaflet'
  import { BAutocomplete } from 'buefy/dist/components/autocomplete'

  import CircleIcon from '@/assets/circle.png'
  import PlusIcon from '@/assets/plus.png'

  const icon = L.icon({
    iconUrl: CircleIcon,
    iconSize: [8, 8], // size of the icon
    iconAnchor: [4, 4], // point of the icon which will correspond to marker's location
  })

  const crosshairIcon = L.icon({
    iconUrl: PlusIcon,
    iconSize: [20, 20], // size of the icon
    iconAnchor: [10, 10], // point of the icon which will correspond to marker's location
  })

  function getPosition(options) {
    return new Promise(function (resolve, reject) {
      navigator.geolocation.getCurrentPosition(resolve, reject, options);
    })
  }

  export default {
    name: 'SelectPoint',
    components: {
      LMap, LTileLayer, LMarker, Portal
    },
    props: {
      stylesheet: {type:String, required: true},
      initialLatitude: {type:Number, required: true},
      initialLongitude: {type:Number, required: true},
    },
    data: function () {
      const center = {lat: this.initialLatitude, lng: this.initialLongitude}
      return {
        // ci: CircleIcon,
        icon: crosshairIcon,
        // finishedLoading: false,
        center: center,
        secondCenter: center,
        zoom: 17,
      }
    },
    async mounted () {
      const map = this.$refs.map.mapObject
      const that = this
      map.on('move', (e) => {
        that.secondCenter=map.getCenter()
      })
    },
    methods: {
      diagnostics () {
        const center = this.$refs.map.mapObject.getCenter()
        return JSON.stringify({center: [center.lat, center.lng]})
      },
    },
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
