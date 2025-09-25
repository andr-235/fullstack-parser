process.env.VK_TOKEN = 'test-token';

const vkApi = require('../../src/repositories/vkApi');

describe('VKApi', () => {
  afterEach(() => {
    jest.restoreAllMocks();
  });

  describe('getPosts', () => {
    it('возвращает объект с постами', async () => {
      const makeRequest = jest
        .spyOn(vkApi, '_makeRequest')
        .mockResolvedValue({
          items: [
            { id: 1, text: 'Post 1', date: 170, likes: { count: 5 } },
            { id: 2, text: 'Post 2', date: 180, likes: { count: 7 } }
          ]
        });

      const result = await vkApi.getPosts(123);

      expect(makeRequest).toHaveBeenCalledWith('wall.get', {
        owner_id: -123,
        count: 10
      });
      expect(result).toEqual({
        posts: [
          expect.objectContaining({ id: 1, likes: 5 }),
          expect.objectContaining({ id: 2, likes: 7 })
        ]
      });
    });

    it('пробрасывает ошибки API', async () => {
      const error = new Error('fail');
      jest.spyOn(vkApi, '_makeRequest').mockRejectedValue(error);

      await expect(vkApi.getPosts(123)).rejects.toThrow('fail');
    });
  });

  describe('getComments', () => {
    it('агрегирует страницы комментариев', async () => {
      const firstPage = {
        items: Array.from({ length: 100 }, (_, idx) => ({
          id: idx + 1,
          text: `Comment ${idx + 1}`,
          from_id: idx,
          date: 1000 + idx,
          likes: { count: idx }
        }))
      };
      const secondPage = {
        items: [{ id: 101, text: 'Comment 101', from_id: 200, date: 2000, likes: { count: 5 } }]
      };

      const makeRequest = jest
        .spyOn(vkApi, '_makeRequest')
        .mockResolvedValueOnce(firstPage)
        .mockResolvedValueOnce(secondPage);

      const result = await vkApi.getComments(123, 1);

      expect(makeRequest).toHaveBeenNthCalledWith(1, 'wall.getComments', {
        owner_id: -123,
        post_id: 1,
        offset: 0,
        count: 100,
        extended: 1,
        fields: 'name'
      });
      expect(makeRequest).toHaveBeenNthCalledWith(2, 'wall.getComments', expect.objectContaining({
        offset: 100
      }));
      expect(result).toEqual({
        comments: expect.arrayContaining([
          expect.objectContaining({ id: 1, text: 'Comment 1' }),
          expect.objectContaining({ id: 2, text: 'Comment 2' }),
          expect.objectContaining({ id: 101, text: 'Comment 101' })
        ]),
        hasMore: false
      });
    });
  });
});