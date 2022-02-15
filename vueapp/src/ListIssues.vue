<template>
  <div>
    <l-map
      ref="map"
      :zoom.sync="zoom"
      :center="center"
      :options="{zoomSnap: 0}"
      :style="{position: 'absolute', height: '' + height + 'px', width: '' + width + 'px'}"
    >
      <l-tile-layer
        url="https://api.mapbox.com/styles/v1/mapbox/streets-v11/tiles/{z}/{x}/{y}?access_token=pk.eyJ1IjoiamVzdmluIiwiYSI6ImNqeDV5emdpeTA2MHI0OG50c2N4OTZhd28ifQ.aehvE-ZEvTy-Yd0yMTSnWw"
        attribution="&copy; <a href=&quot;http://osm.org/copyright&quot;>OpenStreetMap</a> contributors"
        :options="{tileSize: 512, zoomOffset: -1}"
      />
      <l-marker
        v-for="issue of issues"
        :key="issue.id"
        :icon="circleIcon"
        :lat-lng="issue.location"
      >
        <l-popup>
          <a :href="`/issues/${issue.id}?slug=${issue.slug}`">{{ issue.title }}</a>
        </l-popup>
      </l-marker>
      <l-marker
        :icon="crosshairIcon"
        :lat-lng="centerMirror"
      />
      <l-polygon
        :lat-lngs="bounds"
        :fill="false"
        color="#bbb"
      />
    </l-map>
    <portal selector="#sidebar-stuff">
      <div class="buttons">
        <a class="button is-info create-issue-url" :href="`/issues/${centerMirror.lat}/${centerMirror.lng}/create`">
          Report Issue
        </a>
        <a class="button is-info recenter-map-url" :href="recenterUrl">
          Recenter Map
        </a>
      </div>
    </portal>
  </div>
</template>

<script>
import L from 'leaflet'
import kebabCase from 'lodash/kebabCase'
import { Portal } from '@linusborg/vue-simple-portal'
import { LMap, LTileLayer, LMarker, LPopup, LPolygon } from 'vue2-leaflet'

import CircleIcon from '@/assets/circle.png'
import PlusIcon from '@/assets/plus.png'

const icon = L.icon({
  iconUrl: CircleIcon,
  iconSize: [8, 8], // size of the icon
  iconAnchor: [4, 4] // point of the icon which will correspond to marker's location
})

const crosshairIcon = L.icon({
  iconUrl: PlusIcon,
  iconSize: [20, 20], // size of the icon
  iconAnchor: [10, 10] // point of the icon which will correspond to marker's location
})

export default {
  name: 'ListIssues',
  components: {
    LMap, LTileLayer, LMarker, LPolygon, LPopup, Portal
  },
  props: {
    rawIssues: { type: Array, required: true },
    rawBounds: { type: Array, required: true }
  },
  data: function () {
    // eslint-disable-next-line no-undef
    const mapDimensions = getMapDimensions()
    const indiaCenter = { lat: 22.5, lng: 82.5 }
    return {
      circleIcon: icon,
      crosshairIcon: crosshairIcon,
      // Center will not sync hence centerMirror is used to sync
      center: indiaCenter,
      centerMirror: indiaCenter,
      zoom: 17,
      bounds: this.rawBounds,
      issues: this.rawIssues.map(i => ({ ...i, slug: kebabCase(i.title) })),

      width: mapDimensions.width,
      height: mapDimensions.height,

      recenterUrl: ''
    }
  },
  async mounted () {
    window.addEventListener('resize', this.onResize)
    window.listIssues = this
    const map = this.getLeaflet()
    const that = this
    map.on('move zoom', (e) => {
      that.centerMirror = map.getCenter()
    })
    map.on('moveend zoomend', (e) => {
      that.updateRecenterUrl()
    })
    map.fitBounds(L.polyline(this.bounds).getBounds())
  },
  methods: {
    getLeaflet () {
      return this.$refs.map.mapObject
    },
    onResize () {
      // eslint-disable-next-line no-undef
      const shit = getMapDimensions()
      this.width = shit.width
      this.height = shit.height
    },
    updateRecenterUrl () {
      const map = this.getLeaflet()
      const mapCenter = map.getCenter()
      const mapBounds = map.getBounds()
      // Assuming that map width is usually less than its height.
      let distance = parseInt(mapBounds.getNorthWest().distanceTo(mapBounds.getNorthEast()) / 2)
      // Since in a test environment, the map has corners same as each other, it has a distance of 0 and can't be tested
      // istanbul ignore next
      if (distance > 100000) {
        distance = 100000
      }
      this.recenterUrl = `/issues/${mapCenter.lat}/${mapCenter.lng}/${distance}`
    }
  }
}
</script>

<style>
  @import "../node_modules/buefy/dist/buefy.min.css";
  @import "../node_modules/leaflet/dist/leaflet.css";
</style>
