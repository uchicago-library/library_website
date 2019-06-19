import React from 'react';
import ReactDOM from 'react-dom';
import PropTypes from 'prop-types';

const DOM_ELEMENT = document.getElementById('news-feed');

const DEFAULT_VISIBLE = Math.trunc(
  DOM_ELEMENT.getAttribute('data-default-visible'),
);

const INCREMENT_VISIBLE = Math.trunc(
  DOM_ELEMENT.getAttribute('data-increment-visible'),
);

const API_URL = DOM_ELEMENT.getAttribute('data-api-url');

const CATEGORY = DOM_ELEMENT.getAttribute('data-category');

const Article = ({ item, category }) => (
  <article>
    <span className="img-object">
      <a href={item.meta.html_url}>
        <img
          src={(item.thumbnail && item.thumbnail.url) || ''}
          className="article-img"
          alt={item.thumbnail_alt_text || ''}
        />
      </a>
      <span className={`news-category ${category.toLowerCase()}`}>
        {category}
      </span>
    </span>
    <a href={item.meta.html_url}>
      <h2>{item.title}</h2>
    </a>
  </article>
);

Article.defaultProps = {
  category: '',
};

Article.propTypes = {
  item: PropTypes.shape({
    meta: PropTypes.shape({
      html_url: PropTypes.string,
    }),
    categories: PropTypes.arrayOf(PropTypes.string),
    title: PropTypes.string,
    tumbnail: PropTypes.string,
    tumbnail_alt_text: PropTypes.string,
  }).isRequired,
  category: PropTypes.string,
};

const LoadMoreBtn = ({ loadMore }) => (
  <section className="load-footer">
    <button onClick={loadMore} type="button" className="btn btn-info">
      Load more
    </button>
  </section>
);
LoadMoreBtn.propTypes = {
  loadMore: PropTypes.func.isRequired,
};

class NewsFeed extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      items: [],
      visible: DEFAULT_VISIBLE,
    };

    this.loadMore = this.loadMore.bind(this);
  }

  componentDidMount() {
    fetch(API_URL)
      .then(res => res.json())
      .then((res) => {
        this.setState({
          items: CATEGORY
            ? res.items.filter(i => i.categories.includes(CATEGORY))
            : res.items,
        });
      })
      .catch((error) => {
        console.error(error); // eslint-disable-line no-console
      });
  }

  loadMore() {
    this.setState(prev => ({ visible: prev.visible + INCREMENT_VISIBLE }));
  }

  render() {
    const { visible } = this.state;
    const { items } = this.state;
    return (
      <section className="news-feed">
        <div className="tiles" aria-live="polite">
          {items.slice(0, visible).map(item => (
            <Article
              item={item}
              category={item.categories[0] || ''}
              key={item.id}
            />
          ))}
        </div>
        {visible < items.length && <LoadMoreBtn loadMore={this.loadMore} />}
      </section>
    );
  }
}

ReactDOM.render(<NewsFeed />, DOM_ELEMENT);
