<template>
  <b-autocomplete
        :data="data"
        placeholder="Find place by name (ex, Kaloor)"
        field="name"
        :loading="isFetching"
        @typing="getAsyncData"
        @select="option => onSelect(option)"
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
</template>

<script>
import axios from 'axios'
import debounce from 'lodash/debounce'
import { BAutocomplete } from 'buefy/dist/components/autocomplete'

export default {
  name: 'SelectPlace',
  components: {
    BAutocomplete
  },
  props: {
    center: { type: Object, required: true },
    onSelect: { type: Function, required: true }
  },
  data: function () {
    return {
      data: [],
      selected: null,
      isFetching: false
    }
  },
  methods: {
    async rawFetch (name) {
      if (!name.length) {
        this.data = []
        return
      }
      this.isFetching = true
      const response = await axios.get(
        '/api/points/search',
        { params: { term: name, lat: this.center.lat, lng: this.center.lng } }
      )
      this.data = response.data.points
      this.isFetching = false
    },
    getAsyncData: debounce(
      /* istanbul ignore next */
      async function (name) {
        this.rawFetch(name)
      }, 300)
  }
}
</script>

<style>
  @import "../node_modules/buefy/dist/buefy.css";
</style>
