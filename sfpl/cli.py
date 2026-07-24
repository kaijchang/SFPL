"""Command-line interface for the :mod:`sfpl` package."""

import argparse
import getpass
import os
import sys

import requests

from . import exceptions
from .sfpl import Account, AdvancedSearch, Book, Branch, List, Search

ADVANCED_FIELDS = (
    "keyword",
    "author",
    "title",
    "subject",
    "series",
    "award",
    "identifier",
    "region",
    "genre",
    "publisher",
    "callnumber",
)
SEARCH_TYPES = ("keyword", "title", "author", "subject", "tag", "list")
WEEKDAYS = ("Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat")


class CLIError(Exception):
    """An expected command-line usage or operation error."""


def _positive_int(value):
    number = int(value)
    if number < 1:
        raise argparse.ArgumentTypeError("must be at least 1")
    return number


def _add_account_options(parser):
    parser.add_argument(
        "--barcode",
        help="library card barcode (default: SFPL_BARCODE)",
    )


def build_parser():
    """Build and return the top-level argument parser."""
    parser = argparse.ArgumentParser(
        prog="sfpl",
        description="Search and inspect San Francisco Public Library data.",
    )
    commands = parser.add_subparsers(
        dest="command", required=True, title="commands", metavar="COMMAND"
    )

    search = commands.add_parser("search", help="search books or user lists")
    search.add_argument("query", help="search query")
    search.add_argument(
        "--type",
        choices=SEARCH_TYPES,
        default="keyword",
        dest="search_type",
        metavar="TYPE",
        help="search field: {} (default: keyword)".format(", ".join(SEARCH_TYPES)),
    )
    search.add_argument(
        "--format",
        metavar="FORMAT",
        help="filter by media format (e.g. LP, BK, DVD)",
    )
    search.add_argument(
        "--sort",
        metavar="SORT",
        help="sort results (e.g. newly_acquired, relevance)",
    )
    search.add_argument(
        "--on-order",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="filter by on-order status (--on-order or --no-on-order)",
    )
    search.add_argument(
        "--details",
        action="store_true",
        help="include detailed book metadata",
    )
    search.add_argument(
        "--pages",
        type=_positive_int,
        default=1,
        help="number of result pages to request (default: 1)",
    )
    search.set_defaults(handler=_run_search)

    advanced = commands.add_parser(
        "advanced-search", help="search with include/exclude filters"
    )
    advanced.add_argument(
        "--include",
        action="append",
        default=[],
        metavar="FIELD=TERM",
        help="include a field value; may be repeated",
    )
    advanced.add_argument(
        "--exclude",
        action="append",
        default=[],
        metavar="FIELD=TERM",
        help="exclude a field value; may be repeated",
    )
    advanced.add_argument(
        "--match",
        choices=("all", "any"),
        default="all",
        metavar="MODE",
        help="combine included filters: all or any (default: all)",
    )
    advanced.add_argument(
        "--format",
        metavar="FORMAT",
        help="filter by media format (e.g. LP, BK, DVD)",
    )
    advanced.add_argument(
        "--sort",
        metavar="SORT",
        help="sort results (e.g. newly_acquired, relevance)",
    )
    advanced.add_argument(
        "--on-order",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="filter by on-order status (--on-order or --no-on-order)",
    )
    advanced.add_argument(
        "--details",
        action="store_true",
        help="include detailed book metadata",
    )
    advanced.add_argument(
        "--pages",
        type=_positive_int,
        default=1,
        help="number of result pages to request (default: 1)",
    )
    advanced.set_defaults(handler=_run_advanced_search)

    details = commands.add_parser("details", help="get details for a book by ID")
    details.add_argument("id", help="book catalog ID")
    details.set_defaults(handler=_run_details)

    hours = commands.add_parser("branch-hours", help="show a branch's hours")
    hours.add_argument("branch", nargs="+", help="branch name")
    hours.set_defaults(handler=_run_branch_hours)

    account = commands.add_parser(
        "account", help="show read-only account circulation data"
    )
    account_commands = account.add_subparsers(
        dest="account_command",
        required=True,
        title="commands",
        metavar="COMMAND",
    )
    holds = account_commands.add_parser("holds", help="show current holds")
    _add_account_options(holds)
    holds.set_defaults(handler=_run_account)
    checkouts = account_commands.add_parser("checkouts", help="show current checkouts")
    _add_account_options(checkouts)
    checkouts.set_defaults(handler=_run_account)

    return parser


def _collect_results(result_pages):
    results = []
    for page in result_pages:
        results.extend(page)
    return results


def _run_search(args, environ, input_stream):
    del environ, input_stream
    search = Search(
        args.query,
        _type=args.search_type,
        format=args.format,
        sort=args.sort,
        on_order=args.on_order,
    )
    results = _collect_results(search.getResults(pages=args.pages))
    if getattr(args, "details", False):
        for item in results:
            if isinstance(item, Book):
                item._include_details = True
    return results


def _parse_filters(values, operation):
    filters = {}
    for value in values:
        field, separator, term = value.partition("=")
        field = field.strip().lower()
        term = term.strip()
        if not separator or field not in ADVANCED_FIELDS or not term:
            valid = ", ".join(ADVANCED_FIELDS)
            raise CLIError(
                f"invalid {operation} filter {value!r}; expected FIELD=TERM where "
                f"FIELD is one of {valid}"
            )
        key = f"{operation}{field}"
        if key in filters:
            raise CLIError(f"duplicate {operation} filter for field {field!r}")
        filters[key] = term
    return filters


def _run_advanced_search(args, environ, input_stream):
    del environ, input_stream
    filters = _parse_filters(args.include, "include")
    # AdvancedSearch builds its query from the included terms, so a search
    # with only excluded terms produces a malformed, empty query.
    if not filters:
        raise CLIError("advanced-search requires at least one --include")
    filters.update(_parse_filters(args.exclude, "exclude"))
    search = AdvancedSearch(
        exclusive=args.match == "all",
        format=args.format,
        sort=args.sort,
        on_order=args.on_order,
        **filters,
    )
    results = _collect_results(search.getResults(pages=args.pages))
    if getattr(args, "details", False):
        for item in results:
            if isinstance(item, Book):
                item._include_details = True
    return results


def _run_details(args, environ, input_stream):
    del environ, input_stream
    book = Book({"_id": args.id, "title": "", "subtitle": "", "author": ""})
    return {"type": "details", "details": book.getDetails()}


def _run_branch_hours(args, environ, input_stream):
    del environ, input_stream
    branch = Branch(" ".join(args.branch))
    return {"branch": branch.name, "hours": branch.getHours()}


def _account_credentials(args, environ, input_stream):
    barcode = args.barcode or environ.get("SFPL_BARCODE")
    if not barcode:
        raise CLIError("a barcode is required via --barcode or SFPL_BARCODE")

    pin = environ.get("SFPL_PIN")
    # getpass reads from the controlling tty, not input_stream; the isatty
    # check is a proxy to avoid prompting in non-interactive use.
    if not pin and input_stream.isatty():
        pin = getpass.getpass("SFPL PIN: ", stream=sys.stderr)
    if not pin:
        raise CLIError("a PIN is required via SFPL_PIN or an interactive prompt")
    return barcode, pin


def _run_account(args, environ, input_stream):
    barcode, pin = _account_credentials(args, environ, input_stream)
    account = Account(barcode, pin)
    if args.account_command == "holds":
        return account.getHolds()
    return account.getCheckouts()


def _format_details(details):
    brief = details.get("brief", {})
    lines = []
    title = brief.get("title")
    if title:
        lines.append("Title: {}".format(title))
    subtitle = brief.get("subTitle")
    if subtitle:
        lines.append("Subtitle: {}".format(subtitle))
    creators = brief.get("creators", [])
    if creators:
        authors = ", ".join(
            c.get("fullName", "") for c in creators if c.get("fullName")
        )
        if authors:
            lines.append("Author: {}".format(authors))
    fmt = brief.get("format")
    if fmt:
        lines.append("Format: {}".format(fmt))
    pub_date = brief.get("publicationDate")
    if pub_date:
        lines.append("Publication Date: {}".format(pub_date))
    desc = brief.get("description")
    if desc:
        lines.append("Description: {}".format(desc))
    return "\n".join(lines)


def _text_item(item):
    if isinstance(item, Book):
        line = item.title
        if item.subtitle:
            line += ": " + item.subtitle
        if item.author:
            line += " — " + item.author
        if item.status:
            line += f" ({item.status})"
        if getattr(item, "_include_details", False):
            try:
                details = item.getDetails()
                formatted = _format_details(details)
                if formatted:
                    line += "\n" + formatted
            except Exception:
                pass
        return line
    if isinstance(item, List):
        return f"{item.title} — {item.user!s} ({item.itemcount} items)"
    raise TypeError(f"unsupported result type: {type(item).__name__}")


def _render(value, stream):
    if isinstance(value, dict) and value.get("type") == "details":
        formatted = _format_details(value["details"])
        if formatted:
            stream.write(formatted + "\n")
        return

    if isinstance(value, list):
        for item in value:
            stream.write(_text_item(item) + "\n")
        return

    stream.write(value["branch"] + "\n")
    hours = value["hours"]
    for day in WEEKDAYS:
        if day in hours:
            stream.write(f"{day}: {hours[day]}\n")
    for day, slots in hours.items():
        if day not in WEEKDAYS:
            stream.write(f"{day}: {slots}\n")


EXPECTED_ERRORS = (
    exceptions.HoldError,
    exceptions.InvalidSearchType,
    exceptions.LoginError,
    exceptions.MissingFilterTerm,
    exceptions.MissingScriptError,
    exceptions.NoBranchFound,
    exceptions.NotLoggedIn,
)


def _error_message(exc):
    return str(exc) or exc.__class__.__name__


def main(argv=None, stdout=None, stderr=None, environ=None, input_stream=None):
    """Run the CLI and return its process exit status."""
    stdout = stdout or sys.stdout
    stderr = stderr or sys.stderr
    environ = os.environ if environ is None else environ
    input_stream = input_stream or sys.stdin
    args = build_parser().parse_args(argv)

    try:
        result = args.handler(args, environ, input_stream)
        _render(result, stdout)
    except CLIError as exc:
        stderr.write(f"sfpl: error: {exc}\n")
        return 2
    except EXPECTED_ERRORS as exc:
        stderr.write(f"sfpl: error: {_error_message(exc)}\n")
        return 1
    except requests.RequestException as exc:
        stderr.write(f"sfpl: error: network request failed: {exc}\n")
        return 1
    except BrokenPipeError:
        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
