/*
 * Parse a LiveWhale JSON events feed into display-ready events for the
 * Workshops & Events widget. Pure functions with no DOM access, so the
 * same code runs in the browser and in Node tests.
 */
var EventsFeed = (function () {
  var TIME_ZONE = 'America/Chicago';

  var dateFormat = new Intl.DateTimeFormat('en-US', {
    timeZone: TIME_ZONE,
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  });

  var dateKeyFormat = new Intl.DateTimeFormat('en-US', {
    timeZone: TIME_ZONE,
    month: '2-digit',
    day: '2-digit',
    year: 'numeric',
  });

  var timeFormat = new Intl.DateTimeFormat('en-US', {
    timeZone: TIME_ZONE,
    hour: 'numeric',
    minute: '2-digit',
    hour12: true,
  });

  var NAMED_ENTITIES = {
    amp: '&',
    lt: '<',
    gt: '>',
    quot: '"',
    apos: "'",
    nbsp: ' ',
    ndash: '–',
    mdash: '—',
    lsquo: '‘',
    rsquo: '’',
    ldquo: '“',
    rdquo: '”',
    hellip: '…',
  };

  function formatParts(format, date) {
    var parts = {};
    format.formatToParts(date).forEach(function (part) {
      parts[part.type] = part.value;
    });
    return parts;
  }

  // "Nov 6, 2026"
  function formatDate(date) {
    var p = formatParts(dateFormat, date);
    return p.month + ' ' + p.day + ', ' + p.year;
  }

  // "3:00 pm"
  function formatTime(date) {
    var p = formatParts(timeFormat, date);
    return p.hour + ':' + p.minute + ' ' + p.dayPeriod.toLowerCase();
  }

  // "2026-11-06", the calendar date in Chicago, for comparisons.
  function dateKey(date) {
    var p = formatParts(dateKeyFormat, date);
    return p.year + '-' + p.month + '-' + p.day;
  }

  // Parse an ISO 8601 string, or LiveWhale's "YYYY-MM-DD HH:MM:SS" UTC form.
  function parseDate(value, isUtc) {
    if (!value) {
      return null;
    }
    var date = new Date(isUtc ? value.replace(' ', 'T') + 'Z' : value);
    return isNaN(date.getTime()) ? null : date;
  }

  function decodeEntities(text) {
    return text.replace(
      /&(#[0-9]+|#x[0-9a-f]+|[a-z]+);/gi,
      function (entity, name) {
        if (name.charAt(0) === '#') {
          var hex = name.charAt(1) === 'x' || name.charAt(1) === 'X';
          var code = parseInt(name.slice(hex ? 2 : 1), hex ? 16 : 10);
          return code > 0 && code <= 0x10ffff
            ? String.fromCodePoint(code)
            : entity;
        }
        var decoded = NAMED_ENTITIES[name.toLowerCase()];
        return decoded === undefined ? entity : decoded;
      }
    );
  }

  function cleanTitle(title) {
    return decodeEntities(String(title || ''))
      .replace(/\r\n|\r|\n/g, ' ')
      .trim();
  }

  /*
   * Start and end of the event a row belongs to. A multi-day event
   * comes as one row per day, and each row carries the span of the
   * whole event in repeats_start and repeats_end (UTC). A weekly
   * series also fills those fields, but each occurrence has its own
   * id and its own dates, so it is read from date_iso and date2_iso.
   */
  function rowSpan(row) {
    var seriesStart = parseDate(row.repeats_start, true);
    var seriesEnd = parseDate(row.repeats_end, true);
    if (
      !row.repeats &&
      seriesStart &&
      seriesEnd &&
      dateKey(seriesStart) !== dateKey(seriesEnd)
    ) {
      return { start: seriesStart, end: seriesEnd, timed: true };
    }
    return {
      start: parseDate(row.date_iso, false),
      end: parseDate(row.date2_iso, false),
      timed: !row.is_all_day,
    };
  }

  /*
   * Split a feed URL into the URL to request and the number of events
   * to show. LiveWhale's /max/<n> counts rows, and a multi-day event
   * has one row per day, so the limit is applied to events instead.
   */
  function parseFeedUrl(url) {
    var match = /\/max\/([0-9]+)\/?$/.exec(url);
    if (!match) {
      return { requestUrl: url, max: null };
    }
    return {
      requestUrl: url.slice(0, match.index),
      max: parseInt(match[1], 10),
    };
  }

  /*
   * Turn LiveWhale JSON into a sorted list of events to display.
   *
   * Each event has title, link, startDate, startTime, endDate, endTime
   * and multiDay. Missing values are empty strings. Events that have
   * ended before today, or that start more than a year from now, are
   * left out. options.max limits the number of events.
   */
  function parseEvents(feed, now, options) {
    var rows = feed && Array.isArray(feed.data) ? feed.data : [];
    var max = options && options.max != null ? options.max : null;
    var today = dateKey(now);
    var lastDay = Number(today.slice(0, 4)) + 1 + today.slice(4);
    var seen = {};
    var events = [];

    rows.forEach(function (row) {
      if (!row || seen[row.id]) {
        return;
      }
      seen[row.id] = true;

      var span = rowSpan(row);
      if (!span.start) {
        return;
      }
      var startDay = dateKey(span.start);
      var endDay = span.end ? dateKey(span.end) : startDay;
      if (endDay < today || startDay > lastDay) {
        return;
      }

      var startDate = formatDate(span.start);
      var endDate = span.end ? formatDate(span.end) : '';
      events.push({
        sortKey: span.start.getTime(),
        title: startDate + ': ' + cleanTitle(row.title),
        link: typeof row.url === 'string' ? row.url : '',
        startDate: startDate,
        startTime: span.timed ? formatTime(span.start) : '',
        endDate: endDate,
        endTime: span.timed && span.end ? formatTime(span.end) : '',
        multiDay: endDate !== '' && endDate !== startDate,
      });
    });

    events.sort(function (a, b) {
      return a.sortKey - b.sortKey;
    });
    if (max !== null) {
      events = events.slice(0, max);
    }
    return events.map(function (event) {
      delete event.sortKey;
      return event;
    });
  }

  // Only http and https links are rendered.
  function isSafeLink(url) {
    return /^https?:\/\//i.test(url || '');
  }

  return {
    parseFeedUrl: parseFeedUrl,
    parseEvents: parseEvents,
    isSafeLink: isSafeLink,
    decodeEntities: decodeEntities,
  };
})();

if (typeof module !== 'undefined' && module.exports) {
  module.exports = EventsFeed;
}
