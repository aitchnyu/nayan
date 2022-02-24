import { mount } from '@vue/test-utils'
import CreateIssueSelectTags from '../../src/CreateIssueSelectTags'

describe('CreateIssueSelectTags.vue', () => {
  it('Can search tags', async () => {
    const wrapper = mount(CreateIssueSelectTags, {
      propsData: {
        allTags: [{ name: 'Foo 1', slug: 'foo-1' }, { name: 'Foo 2', slug: 'foo-2' }],
        selectedTags: []
      }
    })
    wrapper.vm.newSelectedTags = [{ name: 'Foo 1', slug: 'foo-1' }, { name: 'Foo 2', slug: 'foo-2' }]
    await wrapper.vm.$nextTick()
    expect(wrapper.vm.field).toBe('foo-1,foo-2')
  })
  it('Can provide hidden input field', async () => {
    const wrapper = mount(CreateIssueSelectTags, {
      propsData: {
        allTags: [{ name: 'Foo 1', slug: 'foo-1' }],
        selectedTags: [{ name: 'Foo 1', slug: 'foo-1' }]
      }
    })
    expect(wrapper.vm.field).toBe('foo-1')
  })
})
