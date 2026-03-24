/** @type {import('@docusaurus/plugin-content-docs').SidebarsConfig} */
const sidebars = {
  tutorialSidebar: [
    'intro',
    {
      type: 'category',
      label: 'Core Concepts',
      items: [
        'core-building-blocks',
        'agent-patterns',
        'tool-use',
      ],
    },
    {
      type: 'category',
      label: 'Implementation',
      items: [
        'implementation-overview',
        'integration-strategies',
        'observability',
      ],
    },
    {
      type: 'category',
      label: 'Advanced Topics',
      items: [
        'scaling-patterns',
        'security-considerations',
      ],
    },
  ],
};

export default sidebars;