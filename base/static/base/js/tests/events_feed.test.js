/* eslint-env node */
const test = require('node:test')
const assert = require('node:assert/strict')
const path = require('node:path')
const fs = require('node:fs')

const EventsFeed = require('../events_feed')

function fixture(name) {
  const file = path.join(__dirname, 'fixtures', name)
  return JSON.parse(fs.readFileSync(file, 'utf8'))
}

// Times in the fixtures are in America/Chicago (CDT is UTC-5 until Nov 1,
// 2026, then CST is UTC-6).
const OCT_28_MORNING = new Date('2026-10-28T09:00:00-05:00')

function eventsAt(now, feedName = 'library_group.json', options = {}) {
  return EventsFeed.parseEvents(fixture(feedName), now, options)
}

function findEvent(events, titleSuffix) {
  return events.find(event => event.title.endsWith(titleSuffix))
}

test('a single-day timed event', () => {
  const event = findEvent(
    eventsAt(OCT_28_MORNING),
    'Latex with Overleaf Pro: the Basics',
  )
  assert.deepEqual(event, {
    title: 'Oct 29, 2026: Latex with Overleaf Pro: the Basics',
    link: 'https://events.uchicago.edu/event/281164-latex-with-overleaf-pro-the-basics',
    startDate: 'Oct 29, 2026',
    startTime: '12:00 pm',
    endDate: 'Oct 29, 2026',
    endTime: '1:00 pm',
    multiDay: false,
  })
})

test('an event with no end time has no end date or time', () => {
  const event = findEvent(
    eventsAt(OCT_28_MORNING),
    'Dictaminal Attitudes: Transcribing and Compiling Peter of Blois',
  )
  assert.equal(event.startDate, 'Nov 6, 2026')
  assert.equal(event.startTime, '3:00 pm')
  assert.equal(event.endDate, '')
  assert.equal(event.endTime, '')
  assert.equal(event.multiDay, false)
})

test('an occurrence of a weekly series is a single-day event', () => {
  const events = eventsAt(OCT_28_MORNING, 'weekly_series.json')
  assert.equal(events.length, 2)
  assert.deepEqual(events[0], {
    title: 'Nov 2, 2026: Let’s Talk',
    link: 'https://events.uchicago.edu/live/events/274857-lets-talk',
    startDate: 'Nov 2, 2026',
    startTime: '1:00 pm',
    endDate: 'Nov 2, 2026',
    endTime: '2:00 pm',
    multiDay: false,
  })
  assert.equal(events[1].startDate, 'Nov 9, 2026')
})

test('per-day rows of a multi-day event collapse to one event', () => {
  const rows = fixture('library_group.json').data
  assert.equal(rows.filter(row => row.id === 273314).length, 4)

  const matches = eventsAt(OCT_28_MORNING).filter(event =>
    event.title.includes('Created Equal'),
  )
  assert.equal(matches.length, 1)
  assert.deepEqual(matches[0], {
    title:
      'Sep 8, 2026: Created Equal: The Premises and Promises of the Declaration of Independence',
    link: 'https://events.uchicago.edu/event/273314-created-equal-the-premises-and-promises-of-the',
    startDate: 'Sep 8, 2026',
    startTime: '9:00 am',
    endDate: 'Dec 11, 2026',
    endTime: '4:45 pm',
    multiDay: true,
  })
})

test('an in-progress multi-day event is listed first', () => {
  const events = eventsAt(OCT_28_MORNING)
  assert.match(events[0].title, /^Sep 8, 2026: Created Equal/)
  assert.equal(
    events[1].title,
    'Oct 28, 2026: Snack-Sized AI: Four Ds of AI Fluency',
  )
})

test('events are sorted by start', () => {
  const titles = eventsAt(OCT_28_MORNING).map(event => event.title)
  assert.deepEqual(titles, [
    'Sep 8, 2026: Created Equal: The Premises and Promises of the Declaration of Independence',
    'Oct 28, 2026: Snack-Sized AI: Four Ds of AI Fluency',
    'Oct 29, 2026: Latex with Overleaf Pro: the Basics',
    'Oct 30, 2026: Halloween Costume Contest  at the Maroon Oasis',
    'Nov 4, 2026: Snack-Sized AI: UChicago AI Q & A',
    'Nov 6, 2026: Dictaminal Attitudes: Transcribing and Compiling Peter of Blois',
    'Jan 13, 2027: Snack-Sized AI: Fellowship Applications and Appropriate AI Use',
  ])
})

test('an event that ends today is still listed after its end time', () => {
  const evening = new Date('2026-12-11T20:00:00-06:00')
  const events = eventsAt(evening)
  assert.match(events[0].title, /^Sep 8, 2026: Created Equal/)
  assert.equal(events[0].endDate, 'Dec 11, 2026')
})

test('a single-day event is listed for the rest of its day', () => {
  const evening = new Date('2026-10-28T23:00:00-05:00')
  assert.ok(
    findEvent(eventsAt(evening), 'Snack-Sized AI: Four Ds of AI Fluency'),
  )
})

test('events that have ended are dropped', () => {
  const nextDay = new Date('2026-10-29T00:30:00-05:00')
  const events = eventsAt(nextDay)
  assert.equal(
    findEvent(events, 'Snack-Sized AI: Four Ds of AI Fluency'),
    undefined,
  )

  const afterExhibit = new Date('2026-12-12T09:00:00-06:00')
  const titles = eventsAt(afterExhibit).map(event => event.title)
  assert.deepEqual(titles, [
    'Jan 13, 2027: Snack-Sized AI: Fellowship Applications and Appropriate AI Use',
  ])
})

test('an event without an end is dropped the day after it starts', () => {
  const dayAfter = new Date('2026-11-07T08:00:00-06:00')
  assert.equal(
    findEvent(
      eventsAt(dayAfter),
      'Dictaminal Attitudes: Transcribing and Compiling Peter of Blois',
    ),
    undefined,
  )
})

test('events more than a year away are dropped', () => {
  const yearBefore = new Date('2026-01-12T12:00:00-06:00')
  const events = eventsAt(yearBefore)
  assert.equal(
    findEvent(
      events,
      'Snack-Sized AI: Fellowship Applications and Appropriate AI Use',
    ),
    undefined,
  )
  const dayLater = new Date('2026-01-13T12:00:00-06:00')
  assert.ok(
    findEvent(
      eventsAt(dayLater),
      'Snack-Sized AI: Fellowship Applications and Appropriate AI Use',
    ),
  )
})

test('titles start with the event start date', () => {
  eventsAt(OCT_28_MORNING).forEach(event => {
    assert.ok(event.title.startsWith(event.startDate + ': '), event.title)
  })
})

test('HTML entities in titles are decoded', () => {
  const rows = fixture('library_group.json').data
  assert.ok(
    rows.some(row => row.title === 'Snack-Sized AI: UChicago AI Q &amp; A'),
  )
  assert.ok(
    findEvent(eventsAt(OCT_28_MORNING), 'Snack-Sized AI: UChicago AI Q & A'),
  )
  assert.equal(
    EventsFeed.decodeEntities(
      '&lt;b&gt; &#8217; &#x2019; &rsquo; &bogus; &amp;amp;',
    ),
    '<b> ’ ’ ’ &bogus; &amp;',
  )
})

test('each CR and LF in a title becomes a space', () => {
  const rows = fixture('library_group.json').data
  assert.ok(rows.some(row => row.title.includes('\r\n')))
  assert.ok(
    findEvent(
      eventsAt(OCT_28_MORNING),
      'Halloween Costume Contest  at the Maroon Oasis',
    ),
  )
})

test('canceled events are kept and marked once', () => {
  const rows = fixture('canceled.json').data
  assert.equal(rows[0].title, 'CANCELED: Autumn Carillon Tower Tours')
  assert.equal(rows[2].title, 'Autumn Carillon Tower Tours')

  const titles = eventsAt(OCT_28_MORNING, 'canceled.json').map(
    event => event.title,
  )
  assert.deepEqual(titles, [
    'Oct 28, 2026: Canceled: Autumn Carillon Tower Tours',
    'Oct 29, 2026: Autumn Carillon Tower Tours',
    'Nov 5, 2026: Canceled: Autumn Carillon Tower Tours',
  ])
})

test('is_canceled marks an event when it is 1, true, or "1"', () => {
  const row = fixture('canceled.json').data[1]
  const titleWith = isCanceled => {
    const feed = { data: [{ ...row, is_canceled: isCanceled }] }
    return EventsFeed.parseEvents(feed, OCT_28_MORNING)[0].title
  }
  ;[1, true, '1'].forEach(value => {
    assert.equal(
      titleWith(value),
      'Oct 29, 2026: Canceled: Autumn Carillon Tower Tours',
      String(value),
    )
  })
  ;[null, 0, false, undefined].forEach(value => {
    assert.equal(
      titleWith(value),
      'Oct 29, 2026: Autumn Carillon Tower Tours',
      String(value),
    )
  })
})

test('a leading "Canceled:" or "Cancelled:" in any case is replaced', () => {
  const row = fixture('canceled.json').data[0]
  ;[
    'Cancelled: Autumn Carillon Tower Tours',
    'canceled:Autumn Carillon Tower Tours',
  ].forEach(title => {
    const feed = { data: [{ ...row, title }] }
    assert.equal(
      EventsFeed.parseEvents(feed, OCT_28_MORNING)[0].title,
      'Oct 28, 2026: Canceled: Autumn Carillon Tower Tours',
    )
  })
})

test('the title of an event that is not canceled is unchanged', () => {
  const row = fixture('canceled.json').data[1]
  const feed = {
    data: [{ ...row, title: 'CANCELED: Autumn Carillon Tower Tours' }],
  }
  assert.equal(
    EventsFeed.parseEvents(feed, OCT_28_MORNING)[0].title,
    'Oct 29, 2026: CANCELED: Autumn Carillon Tower Tours',
  )
})

test('max counts events, not rows', () => {
  const rows = fixture('library_group.json').data
  assert.equal(new Set(rows.slice(0, 3).map(row => row.id)).size, 2)

  const events = eventsAt(OCT_28_MORNING, 'library_group.json', { max: 3 })
  assert.deepEqual(
    events.map(event => event.startDate),
    ['Sep 8, 2026', 'Oct 28, 2026', 'Oct 29, 2026'],
  )
})

test('parseFeedUrl removes /max/<n> from the request', () => {
  const base =
    'https://events.uchicago.edu/live/json/events/group/Library/tag/library'
  assert.deepEqual(EventsFeed.parseFeedUrl(base + '/max/5'), {
    requestUrl: base,
    max: 5,
  })
  assert.deepEqual(EventsFeed.parseFeedUrl(base + '/max/12/'), {
    requestUrl: base,
    max: 12,
  })
  assert.deepEqual(EventsFeed.parseFeedUrl(base), {
    requestUrl: base,
    max: null,
  })
})

test('an empty feed has no events', () => {
  assert.deepEqual(eventsAt(OCT_28_MORNING, 'empty.json'), [])
})

test('a feed without a data list has no events', () => {
  assert.deepEqual(EventsFeed.parseEvents(null, OCT_28_MORNING), [])
  assert.deepEqual(EventsFeed.parseEvents({}, OCT_28_MORNING), [])
})

test('only http and https links are safe', () => {
  assert.ok(EventsFeed.isSafeLink('https://events.uchicago.edu/event/1'))
  assert.ok(EventsFeed.isSafeLink('http://events.uchicago.edu/event/1'))
  // eslint-disable-next-line no-script-url
  assert.ok(!EventsFeed.isSafeLink('javascript:alert(1)'))
  assert.ok(!EventsFeed.isSafeLink(''))
  assert.ok(!EventsFeed.isSafeLink(null))
})
