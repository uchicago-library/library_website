/* JSON schema for CGIMail Forms. These are the required fields */

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
};

export default schema;
