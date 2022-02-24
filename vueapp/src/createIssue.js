import CreateIssueSelectPoint from './CreateIssueSelectPoint'
import CreateIssueSelectTags from './CreateIssueSelectTags'
import mountComponent from './mountComponent'

mountComponent(
  CreateIssueSelectPoint,
  // eslint-disable-next-line no-undef
  { center: rawData.center },
  '#select-point')

mountComponent(
  CreateIssueSelectTags,
  // eslint-disable-next-line no-undef
  { allTags: rawData.allTags, selectedTags: rawData.selectedTags },
  '#select-tags')
