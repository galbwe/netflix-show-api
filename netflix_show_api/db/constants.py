"""
Defines constants for constructing database schema.
"""
from typing import Set

TITLE_TYPES = (
    "movie",
    "tv_show",
)


DURATION_UNITS = (
    "minutes",
    "seasons",
)


COUNTRIES = (
    "Afghanistan",
    "Albania",
    "Algeria",
    "Angola",
    "Argentina",
    "Armenia",
    "Australia",
    "Austria",
    "Azerbaijan",
    "Bahamas",
    "Bangladesh",
    "Belarus",
    "Belgium",
    "Bermuda",
    "Botswana",
    "Brazil",
    "Bulgaria",
    "Cambodia",
    "Canada",
    "Cayman Islands",
    "Chile",
    "China",
    "Colombia",
    "Croatia",
    "Cuba",
    "Cyprus",
    "Czech Republic",
    "Denmark",
    "Dominican Republic",
    "East Germany",
    "Ecuador",
    "Egypt",
    "Finland",
    "France",
    "Georgia",
    "Germany",
    "Ghana",
    "Greece",
    "Guatemala",
    "Hong Kong",
    "Hungary",
    "Iceland",
    "India",
    "Indonesia",
    "Iran",
    "Iraq",
    "Ireland",
    "Israel",
    "Italy",
    "Jamaica",
    "Japan",
    "Jordan",
    "Kazakhstan",
    "Kenya",
    "Kuwait",
    "Latvia",
    "Lebanon",
    "Liechtenstein",
    "Lithuania",
    "Luxembourg",
    "Malawi",
    "Malaysia",
    "Malta",
    "Mauritius",
    "Mexico",
    "Mongolia",
    "Montenegro",
    "Morocco",
    "Namibia",
    "Nepal",
    "Netherlands",
    "New Zealand",
    "Nicaragua",
    "Nigeria",
    "Norway",
    "Pakistan",
    "Panama",
    "Paraguay",
    "Peru",
    "Philippines",
    "Poland",
    "Portugal",
    "Puerto Rico",
    "Qatar",
    "Romania",
    "Russia",
    "Samoa",
    "Saudi Arabia",
    "Senegal",
    "Serbia",
    "Singapore",
    "Slovakia",
    "Slovenia",
    "Somalia",
    "South Africa",
    "South Korea",
    "Soviet Union",
    "Spain",
    "Sri Lanka",
    "Sudan",
    "Sweden",
    "Switzerland",
    "Syria",
    "Taiwan",
    "Thailand",
    "Turkey",
    "Uganda",
    "Ukraine",
    "United Arab Emirates",
    "United Kingdom",
    "United States",
    "Uruguay",
    "Vatican City",
    "Venezuela",
    "Vietnam",
    "West Germany",
    "Zimbabwe",
)


RATINGS = (
    "G",
    "NC-17",
    "NR",
    "PG",
    "PG-13",
    "R",
    "TV-14",
    "TV-G",
    "TV-MA",
    "TV-PG",
    "TV-Y",
    "TV-Y7",
    "TV-Y7-FV",
    "UR",
)


GENRES = (
    "Action & Adventure",
    "Anime Features",
    "Anime Series",
    "British TV Shows",
    "Children & Family Movies",
    "Classic & Cult TV",
    "Classic Movies",
    "Comedies",
    "Crime TV Shows",
    "Cult Movies",
    "Documentaries",
    "Docuseries",
    "Dramas",
    "Faith & Spirituality",
    "Horror Movies",
    "Independent Movies",
    "International Movies",
    "International TV Shows",
    "Kids' TV",
    "Korean TV Shows",
    "LGBTQ Movies",
    "Movies",
    "Music & Musicals",
    "Reality TV",
    "Romantic Movies",
    "Romantic TV Shows",
    "Sci-Fi & Fantasy",
    "Science & Nature TV",
    "Spanish-Language TV Shows",
    "Sports Movies",
    "Stand-Up Comedy",
    "Stand-Up Comedy & Talk Shows",
    "TV Action & Adventure",
    "TV Comedies",
    "TV Dramas",
    "TV Horror",
    "TV Mysteries",
    "TV Sci-Fi & Fantasy",
    "TV Shows",
    "TV Thrillers",
    "Teen TV Shows",
    "Thrillers",
)


def create_aliases(constants):
    aliases = set()
    for constant in constants:
        variations = [
            constant,
            constant.replace("&", "And"),
            constant.replace("-", ""),
            constant.replace("-", " "),
        ]
        for variation in variations:
            aliases |= set(
                [
                    (variation, variation),
                    (variation.lower(), variation),
                    (variation.upper(), variation),
                ]
            )
    return tuple(add_specific_aliases(aliases))


def add_specific_aliases(aliases: Set) -> Set:
    aliases.add(("anime", "Anime Series"))
    aliases.add(("Anime", "Anime Series"))
    return aliases


GENRE_ALIASES = create_aliases(GENRES)


COUNTRY_ALIASES = create_aliases(COUNTRIES)


TITLE_TYPE_ALIASES = create_aliases(TITLE_TYPES)


DURATION_UNIT_ALIASES = create_aliases(DURATION_UNITS)


RATING_ALIASES = create_aliases(RATINGS)
