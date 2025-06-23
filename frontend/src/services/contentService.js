// Content service for managing content operations
import { api } from './api';

class ContentService {
  // Fetch content by type
  async getContent(type, params = {}) {
    try {
      const response = await api.get(`/content/${type}`, { params });
      return response.data;
    } catch (error) {
      console.error(`Error fetching ${type} content:`, error);
      throw error;
    }
  }

  // Get case studies
  async getCaseStudies(params = {}) {
    return this.getContent('case-studies', params);
  }

  // Get tutorials
  async getTutorials(params = {}) {
    return this.getContent('tutorials', params);
  }

  // Get documentation
  async getDocumentation(section) {
    try {
      const response = await api.get(`/content/docs/${section}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching documentation for ${section}:`, error);
      throw error;
    }
  }

  // Get example datasets
  async getExampleDatasets(analysisType) {
    try {
      const response = await api.get(`/content/datasets/${analysisType}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching datasets for ${analysisType}:`, error);
      throw error;
    }
  }

  // Get templates
  async getTemplates(templateType) {
    try {
      const response = await api.get(`/content/templates/${templateType}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching templates for ${templateType}:`, error);
      throw error;
    }
  }

  // Get FAQ content
  async getFAQ(category = null) {
    try {
      const params = category ? { category } : {};
      const response = await api.get('/content/faq', { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching FAQ:', error);
      throw error;
    }
  }

  // Get news and updates
  async getNews(params = {}) {
    try {
      const response = await api.get('/content/news', { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching news:', error);
      throw error;
    }
  }

  // Get blog posts
  async getBlogPosts(params = {}) {
    try {
      const response = await api.get('/content/blog', { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching blog posts:', error);
      throw error;
    }
  }

  // Get single blog post
  async getBlogPost(slug) {
    try {
      const response = await api.get(`/content/blog/${slug}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching blog post ${slug}:`, error);
      throw error;
    }
  }

  // Get video tutorials
  async getVideoTutorials(category = null) {
    try {
      const params = category ? { category } : {};
      const response = await api.get('/content/videos', { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching video tutorials:', error);
      throw error;
    }
  }

  // Get research papers
  async getResearchPapers(params = {}) {
    try {
      const response = await api.get('/content/research', { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching research papers:', error);
      throw error;
    }
  }

  // Search content
  async searchContent(query, filters = {}) {
    try {
      const response = await api.post('/content/search', {
        query,
        ...filters
      });
      return response.data;
    } catch (error) {
      console.error('Error searching content:', error);
      throw error;
    }
  }

  // Get content recommendations
  async getRecommendations(contentType, currentId) {
    try {
      const response = await api.get(`/content/recommendations/${contentType}/${currentId}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching recommendations:', error);
      throw error;
    }
  }

  // Track content view
  async trackView(contentType, contentId) {
    try {
      await api.post('/content/track/view', {
        contentType,
        contentId,
        timestamp: new Date().toISOString()
      });
    } catch (error) {
      console.error('Error tracking content view:', error);
      // Don't throw - tracking failures shouldn't break the app
    }
  }

  // Get user's content history
  async getContentHistory() {
    try {
      const response = await api.get('/content/history');
      return response.data;
    } catch (error) {
      console.error('Error fetching content history:', error);
      throw error;
    }
  }

  // Save content for later
  async saveForLater(contentType, contentId) {
    try {
      const response = await api.post('/content/save', {
        contentType,
        contentId
      });
      return response.data;
    } catch (error) {
      console.error('Error saving content:', error);
      throw error;
    }
  }

  // Get saved content
  async getSavedContent() {
    try {
      const response = await api.get('/content/saved');
      return response.data;
    } catch (error) {
      console.error('Error fetching saved content:', error);
      throw error;
    }
  }

  // Remove saved content
  async removeSavedContent(contentId) {
    try {
      await api.delete(`/content/saved/${contentId}`);
    } catch (error) {
      console.error('Error removing saved content:', error);
      throw error;
    }
  }
}

// Create singleton instance
const contentService = new ContentService();

export default contentService;