create table s10_logins (
    id text primary key
);

create table pens (
   id serial primary key,
    image text,
    date text,
    name text,
    text text,
    pen_type text,
    nib_sizes text,
    capped_retractable text,
    barrel_material text,
    length_uncapped_cm text,
    similar_to text,
    street_price text,
    clip text,
    grip_material text,
    grip_diameter_mm text,
    writing_sizes text,
    country_of_origin text,
    manufacturer text,
    refills text,
    barrel_color text,
    still_sold text,
    weight_g text,
    length_capped_retracted_cm text,
    grip_color text,
    refillable text,
    length_posted_cm text,
    nib_color text,
    rating text,
    body_diameter_mm text,
    ink_color_shipped text,
    nib_material text,
    release_year text,
    msrp text
);
-- It's entirely possible I wasted an hour or two scraping a website for this information and built this giant table.
-- don't sweat it, the import field is "text" -- which is the review text. the rest is just, kind, stuff.

-- not strictly required, but it sure speeds things up when we search later!
CREATE INDEX pen_review_search_idx on pens USING GIN (to_tsvector('english', text));


create table pen_likes (
    user_id text,
    pen_id int,
    primary key (user_id, pen_id),
    foreign key (pen_id) REFERENCES pens(id)
);
