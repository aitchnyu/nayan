import { mount } from '@vue/test-utils'
import SelectIssueTags from '../../src/SelectIssueTags'

describe('SelectIssueTags.vue', () => {
  it('Can search and select tags', async () => {
    const wrapper = mount(SelectIssueTags, {
      propsData: {
        tags: [],
        allTags: [{ name: 'Foo 1', slug: 'foo-1' }, { name: 'Foo 2', slug: 'foo-2' }],
        onSelect: () => 1
      }
    })
    await wrapper.vm.getData('')
    await wrapper.vm.$nextTick()
    expect(wrapper.vm.data).toEqual([])
    await wrapper.vm.getData('1')
    await wrapper.vm.$nextTick()
    expect(wrapper.vm.data).toEqual([{ name: 'Foo 1', slug: 'foo-1' }])
  })
})
