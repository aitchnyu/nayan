<template>
  <b-taginput
        :value="tags"
        :data="data"
        :autocomplete="true"
        placeholder=""
        field="name"
        @typing="getData"
        @input="option => onSelect(option)"
      >
        <template slot-scope="props">
          <div class="media">
            <div class="media-content">
              {{ props.option.name }}
              <br>
            </div>
          </div>
        </template>
      </b-taginput>
</template>

<script>
import { BTaginput } from 'buefy/dist/components/taginput'

export default {
  name: 'SelectIssueTags',
  components: {
    BTaginput
  },
  props: {
    tags: { type: Array, required: true },
    allTags: { type: Array, required: true },
    onSelect: { type: Function, required: true }
  },
  data: function () {
    return {
      data: [],
      selected: null
    }
  },
  methods: {
    getData (name) {
      if (!name.length) {
        this.data = []
        return
      }
      this.data = this.allTags.filter(tag => tag.name.toLowerCase().includes(name.toLowerCase()))
    }
  }
}
</script>

<style>
  @import "../node_modules/buefy/dist/buefy.css";
</style>
