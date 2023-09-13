import scrapy
from items import MusicLoopItem, CategoryLoopsItem


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
    MAX_LOOPS_TO_SCRAPE = 100

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
                print(cat_name)

                cat_url = f"https://www.looperman.com/loops?page=1&cid={cat_id}"
                print(f"yielded cat url {cat_url}")
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
        max_count_for_cat = int(
            (self.num_cats_scraped + 1)
            * LoopSpider.MAX_LOOPS_TO_SCRAPE
            / len(LoopSpider.allowed_cats)
        )
        print(f"max count for cat {max_count_for_cat}")
        for i, player_wrapper in enumerate(player_wrappers):
            if self.num_loops_scraped >= max_count_for_cat:
                break
            loop_name = player_wrapper.css("a.player-title::text")
            # pprint(player_wrapper.get())
            print(f"loop name {loop_name.get()}")
            url = player_wrapper.css("::attr(rel)")
            print(f"url {url.get()}")
            description = description_wrappers[i].css("p::text")
            print(f"description {description.get()}")
            genre = tag_wrappers[i].css('a[title^="Genre"]::text')
            print(f"genre {genre.get()}")
            bpm = tag_wrappers[i].css('a[title^="Find more loops at"]::text')
            print(f"bpm {bpm.get()}")
            key = tag_wrappers[i].css('a[title^="This loop is in the key of"]::text')
            print(f'key {"Unknown" if not key else key.get().split()[-1]}')
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
        print(f"num loops scraped {self.num_loops_scraped}")
        next_page = response.css(
            'div.pagination-links a:contains(">")::attr(href)'
        ).get()
        should_go_next = next_page and self.num_loops_scraped < max_count_for_cat
        if should_go_next:
            print("going to next page")
            yield response.follow(
                next_page, callback=self.parse_cat, meta={"cat_name": cat_name}
            )
        else:
            self.num_cats_scraped += 1
            yield this_category_loops
