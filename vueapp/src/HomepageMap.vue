<template>
  <div>
    <div
      v-if="finishedLoading"
      id="finished-loading-indicator"
      style="display: none"
    />
    <div>
      <l-map
        ref="map"
        :zoom.sync="zoom"
        :center="center"
        style="height: 75vh; width: 100%; background-color: #e6e5e0"
      >
        <l-tile-layer
          url="https://api.mapbox.com/styles/v1/mapbox/streets-v11/tiles/{z}/{x}/{y}?access_token=pk.eyJ1IjoiamVzdmluIiwiYSI6ImNqeDV5emdpeTA2MHI0OG50c2N4OTZhd28ifQ.aehvE-ZEvTy-Yd0yMTSnWw"
          attribution="&copy; <a href=&quot;http://osm.org/copyright&quot;>OpenStreetMap</a> contributors"
          :options="{tileSize: 512, zoomOffset: -1}"
        />
        <l-marker
          v-if="userLocationMarker"
          :icon="icon"
          :lat-lng="userLocationMarker"
        >
          <l-tooltip :options="{permanent: true, interactive: true}">
            <a :href="`/issues/${userLocationMarker.lat}/${userLocationMarker.lng}/1000`">Issues at your location</a>
          </l-tooltip>
        </l-marker>
        <l-marker
          :icon="icon"
          :lat-lng="secondCenter"
        >
          <l-tooltip :options="{permanent: true, interactive: true}">
            <a :href="`/issues/${secondCenter.lat}/${secondCenter.lng}/1000`">Issues here</a>
          </l-tooltip>
        </l-marker>
        <l-marker
          v-if="selected"
          :icon="icon"
          :lat-lng="selected.point"
        >
          <l-tooltip :options="{permanent: true, interactive: true}">
            <a :href="`/issues/${selected.point.lat}/${selected.point.lng}/1000`">Issues around {{ selected.name }}</a>
          </l-tooltip>
        </l-marker>
      </l-map>

      <div
        v-if="locationErrorMessage"
        class="panel is-danger"
      >
        <p class="panel-heading">
          Unable to get your location
        </p>
        <div class="panel-block is-active">
          <div>
            Please enable <a
              href="https://www.gps-coordinates.net/geolocation"
              target="_blank"
              class="mx-1"
            >your location services </a> and reload this page.
            The error message was: <span class="has-text-danger mx-1"> {{ locationErrorMessage }} </span>
          </div>
        </div>
      </div>

      <b-autocomplete
        :data="data"
        placeholder="Find place by name (ex, Kaloor)"
        field="name"
        :loading="isFetching"
        @typing="getAsyncData"
        @select="option => selected = option"
      >
        <template slot-scope="props">
          <div class="media">
            <div class="media-content">
              {{ props.option.name }}
              <br>
            </div>
          </div>
        </template>
      </b-autocomplete>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import debounce from 'lodash/debounce'
import L from 'leaflet'
import { LMap, LTileLayer, LMarker, LTooltip } from 'vue2-leaflet'
import { BAutocomplete } from 'buefy/dist/components/autocomplete'

import PlusIcon from '@/assets/plus.png'

const crosshairIcon = L.icon({
  iconUrl: PlusIcon,
  iconSize: [20, 20], // size of the icon
  iconAnchor: [10, 10] // point of the icon which will correspond to marker's location
})

function getPosition (options) {
  return new Promise(function (resolve, reject) {
    navigator.geolocation.getCurrentPosition(resolve, reject, options)
  })
}

export default {
  name: 'HomepageMap',
  components: {
    BAutocomplete, LMap, LTileLayer, LMarker, LTooltip
  },
  data: function () {
    const indiaCenter = { lat: 22.5, lng: 82.5 }
    return {
      // ci: CircleIcon,
      icon: crosshairIcon,
      finishedLoading: false,
      center: indiaCenter,
      secondCenter: indiaCenter,
      zoom: 17,
      // markers: CONSTANTS.markers,
      // extentPoints: CONSTANTS.extent_points,
      userLocationMarker: null,
      locationErrorMessage: null,

      data: [],
      selected: null,
      isFetching: false
    }
  },
  watch: {
    selected: function (newSelected, oldSelected) {
      if (newSelected) {
        this.center = newSelected.point
      }
    }
  },
  async mounted () {
    window.homepageMap = this
    const map = this.getLeaflet()
    const that = this
    map.on('move', (e) => {
      that.secondCenter = map.getCenter()
    })
    map.once('moveend zoomend', () => { this.finishedLoading = true })

    try {
      const location = await getPosition()
      const center = { lat: location.coords.latitude, lng: location.coords.longitude }
      this.userLocationMarker = center
      this.center = center
    } catch (e) {
      // todo reraise
      console.log('no location', e)
      this.locationErrorMessage = e.message
    }
  },
  methods: {
    getLeaflet () {
      return this.$refs.map.mapObject
    },
    diagnostics () {
      const center = this.getLeaflet().getCenter()
      return JSON.stringify({ center: [center.lat, center.lng] })
    },
    createMarker () {
      console.log('create marker', this)
      const mapCenter = this.$refs.map.mapObject.getCenter()
      window.location = `/markers/create/${mapCenter.lat}/${mapCenter.lng}`
    },
    getAsyncData: debounce(async function (name) {
      if (!name.length) {
        this.data = []
        return
      }
      this.isFetching = true
      const response = await axios.get(
        '/api/points/search',
        { params: { term: name, lat: this.center.lat, lng: this.center.lng } }
      )
      console.log(name, response.data.points)
      this.data = response.data.points
      // response.data.results.forEach( i => this.data.push(i))
      this.isFetching = false
    }
    , 300)
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
