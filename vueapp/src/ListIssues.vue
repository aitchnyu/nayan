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
      <l-control position="topleft" class="leaflet-bar">
        <a title="Recenter map" :href="recenterUrl">
          🞖
        </a>
        <a title="Report issue" :href="`/issues/${centerMirror.lat}/${centerMirror.lng}/create`" target="_blank">
          🗋
        </a>
      </l-control>
      <l-marker
        v-for="issue of issues"
        :key="issue.id"
        :icon="circleIcon"
        :lat-lng="issue.location"
      >
        <!-- :lat-lng is present here since leafletMap.openPopup(popup) needs it -->
        <l-popup :ref="`popup-${issue.id}`" :options="{foo:1}" :lat-lng="issue.location">
          <a :href="`/issues/${issue.id}?slug=${issue.slug}`">
            {{ issue.title }}
          </a>
          <div v-for="tag of issue.tags" :key="tag.slug">
            {{ tag.name }}
          </div>
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
    <portal selector="#sidebar-stuff" :prepend="true">
      <div class="show-only-one">
        <div class="buttons">
        <a class="button is-info create-issue-url" :href="`/issues/${centerMirror.lat}/${centerMirror.lng}/create`" target="_blank">
          🗋 Report Issue
        </a>
        <a class="button is-info recenter-map-url" :href="recenterUrl">
          🞖 Recenter Map
        </a>
      </div>
      <div class="field">
        <label class="label">All of these tags</label>
        <select-issue-tags :on-select="tags => updateTagFilters('all', tags)"
                           :tags="tagFilters.all"
                           :all-tags="allTags"/>
      </div>
      <div class="field">
        <label class="label">Any of these tags</label>
        <select-issue-tags :on-select="tags => updateTagFilters('any', tags)"
                           :tags="tagFilters.any"
                           :all-tags="allTags"/>
      </div>
      <div class="field">
        <label class="label">None of these tags</label>
        <select-issue-tags :on-select="tags => updateTagFilters('none', tags)"
                           :tags="tagFilters.none"
                           :all-tags="allTags"/>
      </div>
      <a class="button is-info create-issue-url" v-if="urlForUpdatedTagFilters" :href="urlForUpdatedTagFilters">
          Update Filters
        </a>
      </div>
    </portal>
  </div>
</template>

<script>
import L from 'leaflet'
import kebabCase from 'lodash/kebabCase'
import { Portal } from '@linusborg/vue-simple-portal'
import { LControl, LMap, LTileLayer, LMarker, LPopup, LPolygon } from 'vue2-leaflet'

import SelectIssueTags from './SelectIssueTags'
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

function replaceUrlParams (params) {
  const url = new URL(window.location)
  const searchParams = new URLSearchParams(url.search)
  const merged = { ...Object.fromEntries(searchParams.entries()), page: null, ...params }
  const out = {}
  for (const [key, value] of Object.entries(merged)) {
    if (value !== null) {
      out[key] = value
    }
  }
  return out
}

// Copy pasted from somewhere
// istanbul ignore next
function redirectPath (path = null, search = null) {
  const url = new URL(window.location)
  const finalPath = path === null ? url.pathname : path
  const finalSearch = search === null
    ? url.search : '?' + new URLSearchParams(replaceUrlParams(search)).toString()
  return finalPath + finalSearch
}

export default {
  name: 'ListIssues',
  components: {
    LControl, LMap, LTileLayer, LMarker, LPolygon, LPopup, Portal, SelectIssueTags
  },
  props: {
    allTags: { type: Array, required: true },
    rawIssues: { type: Array, required: true },
    rawBounds: { type: Array, required: true },
    rawFilters: { type: Object, required: true }
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
      tagFilters: this.rawFilters,
      urlForUpdatedTagFilters: null,

      width: mapDimensions.width,
      height: mapDimensions.height,

      recenterUrl: ''
    }
  },
  async mounted () {
    window.addEventListener('resize', this.onResize)
    window.listissues = this
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
    updateTagFilters (field, tags) {
      function removeDuplicateTags (inputTags, checkTags) {
        const checkTagSlugs = checkTags.map(tag => tag.slug)
        return inputTags.filter(tag => checkTagSlugs.indexOf(tag.slug) === -1)
      }
      function joinTagSlugs (tagArray) {
        return tagArray.length ? tagArray.map(tag => tag.slug).join(',') : null
      }
      // There is no else block
      // istanbul ignore else
      if (field === 'all') {
        this.tagFilters.all = tags
        this.tagFilters.any = removeDuplicateTags(this.tagFilters.any, tags)
        this.tagFilters.none = removeDuplicateTags(this.tagFilters.none, tags)
      } else if (field === 'any') {
        this.tagFilters.any = tags
        this.tagFilters.all = removeDuplicateTags(this.tagFilters.all, tags)
        this.tagFilters.none = removeDuplicateTags(this.tagFilters.none, tags)
      } else if (field === 'none') {
        this.tagFilters.none = tags
        this.tagFilters.all = removeDuplicateTags(this.tagFilters.all, tags)
        this.tagFilters.any = removeDuplicateTags(this.tagFilters.any, tags)
      }
      this.urlForUpdatedTagFilters = redirectPath(
        null,
        {
          all_tags: joinTagSlugs(this.tagFilters.all),
          any_tags: joinTagSlugs(this.tagFilters.any),
          none_tags: joinTagSlugs(this.tagFilters.none)
        })
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
      this.recenterUrl = redirectPath(`/issues/${mapCenter.lat}/${mapCenter.lng}/${distance}`, null)
    },
    highlightIssue (id) {
      console.log('highlight', id)
      const foo = this.$refs[`popup-${id}`][0].mapObject
      this.getLeaflet().openPopup(foo)
    }
  }
}
</script>

<style>
  @import "../node_modules/buefy/dist/buefy.min.css";
  @import "../node_modules/leaflet/dist/leaflet.css";

  /* Icon will be tiny otherwise, and cursor won't match the zoom buttons */
  .leaflet-bar a {
    font-size: 22px;
    cursor: pointer;
  }
</style>
