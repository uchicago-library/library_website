/* JSON schema for CGIMail Forms. These are the required fields.
 *
 * Optional properties not validated by this schema but supported:
 * - Section level: hiddenButVisible (bool) - displays fields as read-only definition list
 * - Fieldset/Group/Element level: disabled (bool) - initial disabled state
 * - Fieldset/Group/Element level: enabledWhen (object) - {field: string, value: string}
 * - Fieldset/Group/Element level: disabledWhen (object) - {field: string, value: string}
 */

const schema = {
  required: true,
  type: 'object',
  properties: {
    form: {
      required: true,
      type: 'object',
      properties: {
        sections: {
          required: true,
          type: 'array',
          properties: {
            0: {
              required: true,
              type: 'object',
              properties: {
                hidden: {
                  required: true,
                  enum: [true],
                },
                elements: {
                  required: true,
                  type: 'array',
                  properties: {
                    0: {
                      required: true,
                      type: 'object',
                      properties: {
                        name: {
                          required: true,
                          enum: ['rcpt'],
                        },
                        type: {
                          required: true,
                          enum: ['hidden'],
                        },
                      },
                    },
                  },
                },
              },
            },
          },
        },
      },
    },
  },
}

export default schema
