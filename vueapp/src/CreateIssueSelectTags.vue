<template>
  <div>
    <select-issue-tags :on-select="newSelectedTags => this.newSelectedTags = newSelectedTags"
                       :tags="newSelectedTags"
                       :all-tags="allTags"/>
    Select one or more tags to describe problem
    <div class="tags">
      <span v-for="tag of allTags" :key="tag.slug" class="tag is-light is-large" @click="selectedTags.push(tag)">
        {{ tag.name }}
      </span>
    </div>
    <input
      type="hidden"
      name="tags"
      :value="field"
    >
  </div>
</template>

<script>
import SelectIssueTags from './SelectIssueTags'

function joinTagSlugs (tagArray) {
  return tagArray.length ? tagArray.map(tag => tag.slug).join(',') : null
}

export default {
  name: 'CreateIssueSelectTags',
  components: {
    SelectIssueTags
  },
  props: {
    allTags: { type: Array, required: true },
    selectedTags: { type: Array, required: false }
  },
  watch: {
    newSelectedTags: function (val) {
      this.field = joinTagSlugs(val)
    }
  },
  data: function () {
    return {
      field: joinTagSlugs(this.selectedTags),
      newSelectedTags: this.selectedTags
    }
  }
}
</script>

<style>
  @import "../node_modules/buefy/dist/buefy.css";
</style>
