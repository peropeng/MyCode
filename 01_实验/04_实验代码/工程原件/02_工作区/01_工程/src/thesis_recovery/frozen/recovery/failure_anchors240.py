"""Deterministic anchors from already-public errors and SHA-bound business AST.

This retrieves existing source evidence; it neither generates patches nor claims
causal dependencies. Test, site-package and unknown paths cannot become anchors.
"""
import re


def strings(value, location=()):
    if isinstance(value, str):
        yield location, value
    elif isinstance(value, dict):
        for key, child in value.items():
            yield from strings(child, location + (str(key),))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from strings(child, location + (index,))


def retrieve(index, files, public_failure, initial_index=None):
    frames, attributes, providers, consumers = [], [], [], []
    patterns = (
        re.compile(r'File\s+[\"\']([^\"\'\n]+\.py)[\"\'],\s*line\s+(\d+)'),
        re.compile(r'([^\s\"\'<>]+\.py):(\d+)(?::|\s|$)'),
    )
    missing = re.compile(r"AttributeError:\s*['\"]([A-Za-z_]\w*)['\"] object has no attribute ['\"]([A-Za-z_]\w*)['\"]")
    seen = set()
    for location, text in strings(public_failure):
        for pattern in patterns:
            for match in pattern.finditer(text):
                reported = match.group(1).replace('\\', '/')
                legal = [path for path in files if reported == path or reported.endswith('/'+path)]
                if len(legal) != 1:
                    continue
                path, line = legal[0], int(match.group(2))
                key = (path, line)
                if key in seen:
                    continue
                seen.add(key)
                observed_index = initial_index if location and location[0] == 'initial_public_failure' and initial_index else index
                enclosing = [p for p in observed_index.providers if not p['historical']
                             and p['path'] == path and p['kind'] == 'function_definition'
                             and p['line'] <= line <= p['end_line']]
                if not enclosing:
                    continue
                observed_function = min(enclosing, key=lambda p: p['end_line']-p['line'])
                current_matches = [p for p in index.providers if not p['historical'] and p['path'] == path
                                   and p['kind'] == 'function_definition' and p['symbol'] == observed_function['symbol']]
                if len(current_matches) != 1:
                    continue
                function = current_matches[0]
                frames.append({'public_field': list(location), 'reported_path': reported,
                               'actual_business_path': path, 'reported_line': line,
                               'current_source_sha256': function['source_sha256'],
                               'observed_source_sha256': observed_function['source_sha256'],
                               'historical_line_rebound_by_function_symbol': observed_index is not index,
                               'enclosing_function': function['symbol'],
                               'static_not_causal': True})
                consumers.append({**function, 'kind': 'public_failure_source_function',
                                  'public_failure_line': line})
                reads = [c for c in index.consumers if not c['historical'] and c['path'] == path
                         and function['line'] <= c['line'] <= function['end_line']]
                for consumer in reads:
                    for provider in index.providers:
                        exact = provider['symbol'] == consumer['symbol']
                        possible = (provider['symbol'].rsplit('.', 1)[-1]
                                    == consumer['symbol'].rsplit('.', 1)[-1])
                        if not (exact or possible):
                            continue
                        if (provider['kind'] == 'attribute_assignment'
                                or provider['kind'] == 'function_definition' and '.' in provider['symbol']) and not exact:
                            continue
                        providers.append(provider)
        for match in missing.finditer(text):
            symbol = match.group(1)+'.'+match.group(2)
            attributes.append({'public_field': list(location), 'missing_class_attribute': symbol})
            providers.extend(p for p in index.providers if p['symbol'] == symbol)
            consumers.extend(c for c in index.consumers if not c['historical'] and c['symbol'] == symbol)
    unique = lambda values: list({(v['path'], v['line'], v['end_line'], v['symbol'], v['kind'], v['historical']): v
                                 for v in values}.values())
    return {'public_business_frames': frames, 'public_missing_attributes': attributes,
            'fallback_to_ranked_only': not frames and not attributes,
            'source': 'Already shared complete public failure; actual current business AST; original edit before/after SHA',
            'model_or_gold_calls': 0, 'causal_claim': False}, unique(providers), unique(consumers)
