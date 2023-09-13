import scrapy
from items import MusicLoopItem, CategoryLoopsItem
from math import ceil


class LoopSpider(scrapy.Spider):
    name = "loops"
    start_urls = ["https://www.looperman.com/loops"]
    allowed_cats = {
        "Bass",
        "Bass Guitar",
        "Bass Synth",
        "Bass Wobble",
        "Drum",
        "Flute",
        "Guitar Acoustic",
        "Guitar Electric",
        "Harp",
        "Percussion",
        "Piano",
        "Scratch",
        "Strings",
        "Synth",
        "Violin",
    }
    # allowed_cats = {"Bass", "Bass Guitar", "Bass Synth"}
    MAX_LOOPS_TO_SCRAPE = 30000

    def __init__(self):
        super().__init__()
        self.num_loops_scraped = 0
        self.num_cats_scraped = 0
        self.category_loops = {}

    def parse(self, response, **kwargs):
        cats = response.css('select[name="cid"]')
        for cat in cats.css("option"):
            cat_name = cat.css("::text").get()
            cat_id = cat.css("::attr(value)").get()

            if cat_name in LoopSpider.allowed_cats:
                cat_url = f"https://www.looperman.com/loops?page=1&cid={cat_id}"
                yield scrapy.Request(
                    url=cat_url,
                    callback=self.parse_cat,
                    meta={"cat_name": cat_name},
                )

    def parse_cat(self, response):
        cat_name = response.meta["cat_name"]

        if cat_name not in self.category_loops:
            self.category_loops[cat_name] = CategoryLoopsItem(cat_name, [])
        this_category_loops = self.category_loops[cat_name]

        player_wrappers = response.css("div.player-wrapper")
        description_wrappers = response.css("div.desc-wrapper")
        tag_wrappers = response.css("div.tag-wrapper")
        max_count_for_cat = self.num_loops_scraped + ceil(
            (LoopSpider.MAX_LOOPS_TO_SCRAPE - self.num_loops_scraped)
            / (len(LoopSpider.allowed_cats) - self.num_cats_scraped)
        )

        for i, player_wrapper in enumerate(player_wrappers):
            if self.num_loops_scraped >= max_count_for_cat:
                break
            loop_name = player_wrapper.css("a.player-title::text")
            url = player_wrapper.css("::attr(rel)")
            description = description_wrappers[i].css("p::text")
            genre = tag_wrappers[i].css('a[title^="Genre"]::text')
            bpm = tag_wrappers[i].css('a[title^="Find more loops at"]::text')
            key = tag_wrappers[i].css('a[title^="This loop is in the key of"]::text')

            this_loop_data = MusicLoopItem(
                name=loop_name.get(),
                url=url.get(),
                description=description.get(),
                genre=genre.get(),
                bpm=int(bpm.get().split()[0]),
                key="Unknown" if not key else key.get().split()[-1],
            )
            yield {
                "file_urls": [this_loop_data.url],
                "name": this_loop_data.name,
                "genre": this_loop_data.genre,
                "cat": cat_name,
            }

            this_category_loops.loops.append(this_loop_data)
            self.num_loops_scraped += 1
        next_page = response.css(
            'div.pagination-links a:contains(">")::attr(href)'
        ).get()
        should_go_next = next_page and self.num_loops_scraped < max_count_for_cat
        if should_go_next:
            yield response.follow(
                next_page, callback=self.parse_cat, meta={"cat_name": cat_name}
            )
        else:
            self.num_cats_scraped += 1
            yield this_category_loops
