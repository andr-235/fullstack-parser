const nock = require('nock');
const axios = require('axios');
const { getPosts, getComments } = require('../../src/repositories/vkApi');

jest.mock('axios');

describe('VKApi', () => {
  const mockToken = 'test-token';
  const mockGroupId = -123;

  beforeEach(() => {
    jest.clearAllMocks();
    nock.cleanAll();
  });

  afterEach(() => {
    nock.cleanAll();
  });

  describe('getPosts', () => {
    it('should fetch and map posts from VK API', async () => {
      const mockResponse = {
        response: {
          items: [
            { id: 1, text: 'Post 1' },
            { id: 2, text: 'Post 2' }
          ]
        }
      };
      axios.get.mockResolvedValue({ data: mockResponse });

      const result = await getPosts(mockGroupId, mockToken);

      expect(axios.get).toHaveBeenCalledWith(
        expect.stringContaining('https://api.vk.com/method/wall.get'),
        expect.objectContaining({
          params: expect.objectContaining({
            owner_id: mockGroupId,
            access_token: mockToken,
            v: '5.131'
          })
        })
      );
      expect(result).toEqual([
        expect.objectContaining({ id: 1, text: 'Post 1' }),
        expect.objectContaining({ id: 2, text: 'Post 2' })
      ]);
    });

    it('should handle API error', async () => {
      axios.get.mockRejectedValue(new Error('VK API error'));

      await expect(getPosts(mockGroupId, mockToken)).rejects.toThrow('VK API error');
    });
  });

  describe('getComments', () => {
    it('should fetch comments from multiple pages', async () => {
      const firstPage = {
        response: {
          items: [{ id: 1, text: 'Comment 1' }, { id: 2, text: 'Comment 2' }],
          count: 150
        }
      };
      const secondPage = {
        response: {
          items: [{ id: 101, text: 'Comment 101' }],
          count: 150
        }
      };

      nock('https://api.vk.com')
        .get('/method/wall.getComments')
        .query({ offset: 0, count: 100, owner_id: mockGroupId, post_id: 1, access_token: mockToken, v: '5.131' })
        .reply(200, firstPage);

      nock('https://api.vk.com')
        .get('/method/wall.getComments')
        .query({ offset: 100, count: 100, owner_id: mockGroupId, post_id: 1, access_token: mockToken, v: '5.131' })
        .reply(200, secondPage);

      const result = await getComments(mockGroupId, 1, mockToken);

      expect(result).toHaveLength(3);
      expect(result).toEqual(
        expect.arrayContaining([
          expect.objectContaining({ id: 1, text: 'Comment 1' }),
          expect.objectContaining({ id: 2, text: 'Comment 2' }),
          expect.objectContaining({ id: 101, text: 'Comment 101' })
        ])
      );
    });
  });
});