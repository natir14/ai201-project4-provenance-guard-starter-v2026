"""
What your test runs. <- UNIT 8, MILESTONE 3

Each of the five criteria in criteria.md, and what is sent to test it.
`run_eval.py` runs every scenario here three times.

PROVENANCE -- read before trusting any result:

  * HUMAN texts come from Project Gutenberg: public-domain books written by
    people long before AI text generation. Each is the FIRST paragraph at or
    after 40% of the way through its book with 100-250 words and at least 3
    sentences -- a rule fixed before any text was scored. The URL, paragraph
    index and SHA-256 of the downloaded file sit next to each one. They are
    19th-century prose: genuinely human, but not representative of modern
    writers, and GPT-2 may have seen these books in training.
  * AI texts were written by Claude (Claude Code) for this test on
    2026-11-08, except the c3-labels candidates marked otherwise. None of
    them is human writing.
  * Nothing here is the student's own writing, so criterion 1 as originally
    written ("my own human-written text") can't be evaluated -- see the
    revision in criteria.md.
  * Criterion 4 (appeals) is not here: run_eval.py only sends /submit. It
    runs from eval_appeals.py instead.

Scenario names stay unique in their first 12 characters, because run_eval.py
builds creator_ids from them (eval_<name[:12]>_<i>) and the rate limit counts
per creator_id.
"""

SCENARIOS = [
    {
        "name": "c1r2-human",
        "criterion": "1 (revised) and 2",
        # 10 human-written passages from Project Gutenberg (public domain).
        "texts": [
            # #1342 Pride and Prejudice -- Jane Austen. https://www.gutenberg.org/cache/epub/1342/pg1342.txt
            # paragraph 1008 of 2511; file sha256 3f6bb9d6f78e0293b56acd4714dd68cb7d6d1d293402031ce9d5a216bcaf9d75
            'Mrs. Bennet was, in fact, too much overpowered to say a great deal while Sir William remained; but no sooner had he left them than her feelings found a rapid vent. In the first place, she persisted in disbelieving the whole of the matter; secondly, she was very sure that Mr. Collins had been taken in; thirdly, she trusted that they would never be happy together; and, fourthly, that the match might be broken off. Two inferences, however, were plainly deduced from the whole: one, that Elizabeth was the real cause of all the mischief; and the other, that she herself had been barbarously used by them all; and on these two points she principally dwelt during the rest of the day. Nothing could console and nothing appease her. Nor did that day wear out her resentment. A week elapsed before she could see Elizabeth without scolding her: a month passed away before she could speak to Sir William or Lady Lucas without being rude; and many months were gone before she could at all forgive their daughter.',
            # #74 The Adventures of Tom Sawyer, Complete -- Mark Twain. https://www.gutenberg.org/cache/epub/74/pg74.txt
            # paragraph 879 of 2104; file sha256 74d77384b123a6360db9ab58463cff8b38df8525fbdc6000c81ee388e1f3cf10
            'Tom quailed. But presently the temptation rose up strong again and the boys agreed to try, with the understanding that they would take to their heels if the snoring stopped. So they went tiptoeing stealthily down, the one behind the other. When they had got to within five steps of the snorer, Tom stepped on a stick, and it broke with a sharp snap. The man moaned, writhed a little, and his face came into the moonlight. It was Muff Potter. The boys’ hearts had stood still, and their hopes too, when the man moved, but their fears passed away now. They tip-toed out, through the broken weather-boarding, and stopped at a little distance to exchange a parting word. That long, lugubrious howl rose on the night air again! They turned and saw the strange dog standing within a few feet of where Potter was lying, and _facing_ Potter, with his nose pointing heavenward.',
            # #1661 The Adventures of Sherlock Holmes -- Arthur Conan Doyle. https://www.gutenberg.org/cache/epub/1661/pg1661.txt
            # paragraph 1029 of 2548; file sha256 922e2a12ccb43a4c9544c260b2166c6ad2097aeb5957faeee113f173bb857cd0
            'It seems that it was. She had the surest information that of late he had, when the fit was on him, made use of an opium den in the farthest east of the City. Hitherto his orgies had always been confined to one day, and he had come back, twitching and shattered, in the evening. But now the spell had been upon him eight-and-forty hours, and he lay there, doubtless among the dregs of the docks, breathing in the poison or sleeping off the effects. There he was to be found, she was sure of it, at the Bar of Gold, in Upper Swandam Lane. But what was she to do? How could she, a young and timid woman, make her way into such a place and pluck her husband out from among the ruffians who surrounded him?',
            # #345 Dracula -- Bram Stoker. https://www.gutenberg.org/cache/epub/345/pg345.txt
            # paragraph 889 of 2192; file sha256 96cd16eacdbfebae8fdda5591f66e0cc8ee76be18e0cd1aca02bc00615782d28
            'I noticed that Van Helsing never kept far away. This was possible from the disordered state of things in the household. There were no relatives at hand; and as Arthur had to be back the next day to attend at his father’s funeral, we were unable to notify any one who should have been bidden. Under the circumstances, Van Helsing and I took it upon ourselves to examine papers, etc. He insisted upon looking over Lucy’s papers himself. I asked him why, for I feared that he, being a foreigner, might not be quite aware of English legal requirements, and so might in ignorance make some unnecessary trouble. He answered me:--',
            # #205 Walden, and On The Duty Of Civil Disobedience -- Henry David Thoreau. https://www.gutenberg.org/cache/epub/205/pg205.txt
            # paragraph 238 of 587; file sha256 2d9a76a2e3e8195c69430516ebd33c4d0757a53ad432ff6186b7b794e6fe99f9
            'I had three chairs in my house; one for solitude, two for friendship, three for society. When visitors came in larger and unexpected numbers there was but the third chair for them all, but they generally economized the room by standing up. It is surprising how many great men and women a small house will contain. I have had twenty-five or thirty souls, with their bodies, at once under my roof, and yet we often parted without being aware that we had come very near to one another. Many of our houses, both public and private, with their almost innumerable apartments, their huge halls and their cellars for the storage of wines and other munitions of peace, appear to me extravagantly large for their inhabitants. They are so vast and magnificent that the latter seem to be only vermin which infest them. I am surprised when the herald blows his summons before some Tremont or Astor or Middlesex House, to see come creeping out over the piazza for all inhabitants a ridiculous mouse, which soon again slinks into some hole in the pavement.',
            # #23 Narrative of the Life of Frederick Douglass, an American Slave -- Frederick Douglass. https://www.gutenberg.org/cache/epub/23/pg23.txt
            # paragraph 92 of 231; file sha256 234c15348a66919bad1d534cdd48ee8ddf91f50115a706cbefaa8edd049672fd
            'Mr. and Mrs. Auld were both at home, and met me at the door with their little son Thomas, to take care of whom I had been given. And here I saw what I had never seen before; it was a white face beaming with the most kindly emotions; it was the face of my new mistress, Sophia Auld. I wish I could describe the rapture that flashed through my soul as I beheld it. It was a new and strange sight to me, brightening up my pathway with the light of happiness. Little Thomas was told, there was his Freddy,—and I was told to take care of little Thomas; and thus I entered upon the duties of my new home with the most cheering prospect ahead.',
            # #2376 Up from Slavery: An Autobiography -- Booker T. Washington. https://www.gutenberg.org/cache/epub/2376/pg2376.txt
            # paragraph 262 of 656; file sha256 084e7f54e60b9ae26ecf2ab23f1789db44d926c3b02106a984f475f9ccc7bdbe
            'The school was constantly growing in numbers, so much so that, after we had got the farm paid for, the cultivation of the land begun, and the old cabins which we had found on the place somewhat repaired, we turned our attention toward providing a large, substantial building. After having given a good deal of thought to the subject, we finally had the plans drawn for a building that was estimated to cost about six thousand dollars. This seemed to us a tremendous sum, but we knew that the school must go backward or forward, and that our work would mean little unless we could get hold of the students in their home life.',
            # #1400 Great Expectations -- Charles Dickens. https://www.gutenberg.org/cache/epub/1400/pg1400.txt
            # paragraph 1567 of 3916; file sha256 9a637118af8e953e9764ec603d9b0a032883384d465acac2e27966a80cf1c6f8
            'It happened that the other five children were left behind at the dinner-table, through Flopson’s having some private engagement, and their not being anybody else’s business. I thus became aware of the mutual relations between them and Mr. Pocket, which were exemplified in the following manner. Mr. Pocket, with the normal perplexity of his face heightened and his hair rumpled, looked at them for some minutes, as if he couldn’t make out how they came to be boarding and lodging in that establishment, and why they hadn’t been billeted by Nature on somebody else. Then, in a distant Missionary way he asked them certain questions,—as why little Joe had that hole in his frill, who said, Pa, Flopson was going to mend it when she had time,—and how little Fanny came by that whitlow, who said, Pa, Millers was going to poultice it when she didn’t forget. Then, he melted into parental tenderness, and gave them a shilling apiece and told them to go and play; and then as they went out, with one very strong effort to lift himself up by the hair he dismissed the hopeless subject.',
            # #84 Frankenstein; or, The modern Prometheus -- Mary Wollstonecraft Shelley. https://www.gutenberg.org/cache/epub/84/pg84.txt
            # paragraph 319 of 798; file sha256 2b97b7f8aad508649481d8dd4f6b54f9b965ddb3ba634e9151c815f537b49e42
            'As he said this he led the way across the ice; I followed. My heart was full, and I did not answer him, but as I proceeded, I weighed the various arguments that he had used and determined at least to listen to his tale. I was partly urged by curiosity, and compassion confirmed my resolution. I had hitherto supposed him to be the murderer of my brother, and I eagerly sought a confirmation or denial of this opinion. For the first time, also, I felt what the duties of a creator towards his creature were, and that I ought to render him happy before I complained of his wickedness. These motives urged me to comply with his demand. We crossed the ice, therefore, and ascended the opposite rock. The air was cold, and the rain again began to descend; we entered the hut, the fiend with an air of exultation, I with a heavy heart and depressed spirits. But I consented to listen, and seating myself by the fire which my odious companion had lighted, he thus began his tale.',
            # #768 Wuthering Heights -- Emily Brontë. https://www.gutenberg.org/cache/epub/768/pg768.txt
            # paragraph 793 of 1980; file sha256 e533fe750589f0421d5d744576315f5c2b9b0d69e981179ea0551bbf134c5e02
            'The sun set behind the Grange as we turned on to the moors; by that, I judged it to be six o’clock; and my companion halted half an hour, to inspect the park, and the gardens, and, probably, the place itself, as well as he could; so it was dark when we dismounted in the paved yard of the farmhouse, and your old fellow-servant, Joseph, issued out to receive us by the light of a dip candle. He did it with a courtesy that redounded to his credit. His first act was to elevate his torch to a level with my face, squint malignantly, project his under-lip, and turn away. Then he took the two horses, and led them into the stables; reappearing for the purpose of locking the outer gate, as if we lived in an ancient castle.',
        ],
    },
    {
        "name": "c2-ai",
        "criterion": 2,
        # 10 AI-generated texts, written by Claude for this test.
        "texts": [
            'Remote work has transformed the way organizations operate, offering employees greater flexibility and autonomy. By eliminating daily commutes, workers can reclaim valuable time and achieve a healthier work-life balance. However, remote work also presents unique challenges, including feelings of isolation and difficulties in maintaining clear communication. To address these issues, companies can invest in collaborative tools, schedule regular virtual check-ins, and foster a strong sense of team culture. Ultimately, a thoughtful approach to remote work can benefit both employees and employers alike.',
            'Getting enough quality sleep is essential for both physical and mental well-being. Research consistently shows that adults who sleep seven to nine hours per night experience improved concentration, better mood regulation, and a stronger immune system. Establishing a consistent sleep schedule, limiting screen time before bed, and creating a calm sleeping environment can significantly enhance sleep quality. Additionally, reducing caffeine intake in the afternoon may help individuals fall asleep more easily. By prioritizing rest, people can unlock their full potential throughout the day.',
            'As climate change accelerates, cities around the world are seeking innovative ways to adapt. Green roofs, expanded tree canopies, and permeable pavements can help reduce urban heat and manage stormwater more effectively. Furthermore, investing in resilient infrastructure ensures that communities are better prepared for extreme weather events. Public engagement also plays a crucial role, as residents who understand the risks are more likely to support adaptation measures. Together, these strategies can help create cities that are safer, healthier, and more sustainable for future generations.',
            'Learning a new language is a rewarding journey that opens doors to new cultures and opportunities. Consistent practice is key, whether through daily vocabulary review, conversation with native speakers, or immersive media such as films and podcasts. Setting achievable goals can help learners stay motivated and track their progress over time. It is also important to embrace mistakes as a natural part of the learning process. With patience and dedication, anyone can develop meaningful proficiency in a second language.',
            'Creating a personal budget is one of the most effective steps toward achieving financial stability. By tracking income and expenses, individuals gain a clear understanding of where their money is going each month. A popular approach is the fifty-thirty-twenty rule, which allocates income to needs, wants, and savings. Additionally, building an emergency fund can provide a valuable safety net during unexpected situations. Over time, disciplined budgeting empowers people to reduce debt, save for the future, and make confident financial decisions.',
            'Reading regularly offers a wide range of benefits that extend far beyond entertainment. Engaging with books can improve vocabulary, strengthen critical thinking skills, and enhance empathy by exposing readers to diverse perspectives. Studies also suggest that reading before bed can reduce stress and promote relaxation. Whether someone prefers fiction, biographies, or scientific nonfiction, making time for reading can enrich daily life. Ultimately, cultivating a reading habit is a simple yet powerful investment in personal growth and lifelong learning.',
            'In an increasingly digital world, practicing good cybersecurity habits is more important than ever. Using strong, unique passwords for each account can significantly reduce the risk of unauthorized access. Enabling two-factor authentication adds an additional layer of protection, while keeping software up to date helps defend against known vulnerabilities. Individuals should also remain cautious of suspicious emails and links, as phishing attacks continue to grow more sophisticated. By adopting these practices, people can better safeguard their personal information and online identities.',
            'Volunteering is a meaningful way to give back to the community while also gaining valuable personal benefits. By contributing time and skills to local organizations, volunteers can make a tangible difference in the lives of others. Volunteering also provides opportunities to develop new skills, expand professional networks, and build lasting friendships. Research has shown that people who volunteer often report higher levels of happiness and life satisfaction. Whether helping at a food bank or mentoring young people, every contribution has a positive impact.',
            'Renewable energy sources such as solar, wind, and hydroelectric power are playing an increasingly vital role in the global transition away from fossil fuels. These technologies produce electricity with minimal greenhouse gas emissions, helping to combat climate change. In recent years, falling costs and technological advancements have made renewable energy more accessible than ever before. Governments and businesses alike are investing heavily in clean energy infrastructure. As adoption continues to grow, renewable energy promises a cleaner, more sustainable future for everyone.',
            'Spending time in nature offers numerous benefits for both mental and physical health. Activities such as hiking, gardening, or simply walking in a park can reduce stress levels and improve overall mood. Exposure to natural environments has also been linked to increased creativity and better concentration. Furthermore, outdoor activities encourage physical movement, which supports cardiovascular health and overall fitness. By making a conscious effort to connect with nature regularly, individuals can enhance their well-being and find a greater sense of balance in their lives.',
        ],
    },
    {
        "name": "c3-labels",
        "criterion": 3,
        # 3 candidates per label, chosen to land in each band. Provenance per text.
        "texts": [
            # -- human candidates --
            # Claude-written; scored human (0.1277) live on 2026-11-01
            "Grandmother's pantry smelled of quince, kerosene and the ghost of a cigar nobody admitted to smoking. Tins without labels. A taxidermied stoat wearing, for reasons never explained, a crocheted waistcoat in mustard wool, presided over the pickled walnuts like a magistrate. Once, aged nine, I unscrewed a jar marked SPARE TEETH and found buttons inside, hundreds of them, horn and jet and mother-of-pearl, each stitched to a scrap of card bearing a date and a single surname. I have never asked whose.",
            # human-written: Gutenberg #205 Walden, and On The Duty Of Civil Disobedience, paragraph 238
            'I had three chairs in my house; one for solitude, two for friendship, three for society. When visitors came in larger and unexpected numbers there was but the third chair for them all, but they generally economized the room by standing up. It is surprising how many great men and women a small house will contain. I have had twenty-five or thirty souls, with their bodies, at once under my roof, and yet we often parted without being aware that we had come very near to one another. Many of our houses, both public and private, with their almost innumerable apartments, their huge halls and their cellars for the storage of wines and other munitions of peace, appear to me extravagantly large for their inhabitants. They are so vast and magnificent that the latter seem to be only vermin which infest them. I am surprised when the herald blows his summons before some Tremont or Astor or Middlesex House, to see come creeping out over the piazza for all inhabitants a ridiculous mouse, which soon again slinks into some hole in the pavement.',
            # human-written: Gutenberg #84 Frankenstein; or, The modern Prometheus, paragraph 319
            'As he said this he led the way across the ice; I followed. My heart was full, and I did not answer him, but as I proceeded, I weighed the various arguments that he had used and determined at least to listen to his tale. I was partly urged by curiosity, and compassion confirmed my resolution. I had hitherto supposed him to be the murderer of my brother, and I eagerly sought a confirmation or denial of this opinion. For the first time, also, I felt what the duties of a creator towards his creature were, and that I ought to render him happy before I complained of his wickedness. These motives urged me to comply with his demand. We crossed the ice, therefore, and ascended the opposite rock. The air was cold, and the rain again began to descend; we entered the hut, the fiend with an air of exultation, I with a heavy heart and depressed spirits. But I consented to listen, and seating myself by the fire which my odious companion had lighted, he thus began his tale.',
            # -- unsure candidates: Claude-written, each scored unsure live before --
            'Our street floods every October, and everyone pretends to be surprised. The council sends a letter, the letter blames the leaves, and the leaves keep falling anyway. Last year Mr. Okafor built a small wall of sandbags and painted them blue, which did nothing for the water but made the whole block laugh for a week. This year the children are planning a raft. I have told them it will sink, and they have told me that is the point.',
            "I started keeping a notebook last spring because my memory for small things was going. At first it was only lists, groceries and phone numbers and the names of my neighbour's dogs. Then it turned into something else, a place where I argued with myself about books I had not finished. Some pages are just one sentence. Others run on for three pages about a bus driver who sang. I do not reread it often, but when I do I barely recognise the person writing.",
            'In the modern workplace, effective communication has become an essential skill for teams of every size. By setting clear expectations, sharing updates regularly, and listening actively, colleagues can significantly reduce misunderstandings. Furthermore, adopting shared tools such as project boards and team chat can help keep everyone aligned. Ultimately, strong communication not only improves results but also builds trust and supports a healthier working environment.',
            # -- AI candidates: Claude-written --
            # scored AI (0.6618) live on 2026-11-01
            "In today's fast-paced world, effective time management has become an essential skill for students and professionals alike. By prioritizing tasks, setting clear goals, and minimizing distractions, individuals can significantly enhance their productivity. Furthermore, adopting tools such as digital calendars and task management applications can help streamline daily routines. Ultimately, mastering time management not only improves performance but also reduces stress and promotes a healthier work-life balance.",
            # scored AI (0.8475) live on 2026-11-01
            'The system is good. The system is fast. The system is easy to use. The system is good for users. The system is fast for users. The system is easy for users. The system is good and fast. The system is easy and good. The system is fast and easy. The system is good for all users and the system is easy for all users.',
            # new, same pattern as the one above
            'The app is simple. The app is quick. The app is easy to learn. The app is simple for everyone. The app is quick for everyone. The app is easy for everyone. The app is simple and quick. The app is quick and easy. The app is easy and simple. The app is simple for all people and the app is quick for all people.',
        ],
    },
    {
        "name": "c5-invalid",
        "criterion": 5,
        # The five invalid submissions criterion 5 names, sent exactly as written.
        # Each has its own creator_id so the rate limit can't mask validation.
        "bodies": [
            {"text": "", "creator_id": "eval_c5_empty"},
            {"creator_id": "eval_c5_missing"},
            {"text": None, "creator_id": "eval_c5_null"},
            {"text": 12345, "creator_id": "eval_c5_numeric"},
            {"text": "word " * 4001, "creator_id": "eval_c5_oversized"},   # 20,005 characters
        ],
    },
]

def validate() -> list[str]:
    """
    Complain about anything malformed, before a long run rather than during.

    A "bodies" scenario is deliberately exempt from the empty check — an empty
    string is the whole point of a bad-input case, and refusing to run one
    would make that criterion untestable.
    """
    problems = []
    for i, scenario in enumerate(SCENARIOS, 1):
        if not scenario.get("name"):
            problems.append(f"scenario {i} has no name")

        texts = scenario.get("texts")
        bodies = scenario.get("bodies")

        if texts and bodies:
            problems.append(
                f"scenario {i} ('{scenario.get('name')}') has both texts and "
                f"bodies — pick one"
            )
            continue

        if bodies:
            for j, body in enumerate(bodies, 1):
                if not isinstance(body, dict):
                    problems.append(
                        f"scenario {i}, body {j} is not a dict — bodies are whole "
                        f"request bodies, like {{'text': '', 'creator_id': 'x'}}"
                    )
            continue

        if not texts:
            problems.append(f"scenario {i} has no texts and no bodies")
            continue

        for j, text in enumerate(texts, 1):
            if not str(text).strip():
                problems.append(
                    f"scenario {i}, text {j} is empty — if an empty submission is what "
                    f"you're testing, use 'bodies' instead of 'texts'"
                )
            elif str(text).startswith("REPLACE ME"):
                problems.append(
                    f"scenario {i} ('{scenario.get('name')}'), text {j} is still "
                    f"the placeholder"
                )
    return problems
