# Testing Guide - Fuzzy Conflict Search

## Overview

This guide demonstrates the fuzzy matching search functionality with accent normalization for the Professional Hubs Conflict API.

---

## Test Cases: Accent Normalization

### Test 1: José = Jose (Accent Removal)

**Input:**
```json
{
  "nombre": "José",
  "apellido": "García"
}
```

**Should Match:**
- Jose García (exact without accent)
- JOSÉ GARCÍA (uppercase with accent)
- jose garcia (lowercase without accent)
- José Garcia (mixed)

**Confidence:**
- All matches should be **100%** (exact match after normalization)
- **Level:** alta

---

### Test 2: María = Maria (Accent Removal)

**Input:**
```json
{
  "nombre": "María",
  "apellido": "Rodríguez"
}
```

**Should Match:**
- Maria Rodriguez
- MARÍA RODRÍGUEZ
- maria rodriguez
- María Rodriguez (mixed)

**Confidence:**
- All matches should be **100%**
- **Level:** alta

---

### Test 3: González = Gonzalez (Accent Removal)

**Input:**
```json
{
  "nombre": "Juan",
  "apellido": "González"
}
```

**Should Match:**
- Juan Gonzalez
- JUAN GONZÁLEZ
- juan gonzalez

**Confidence:**
- All matches should be **100%**
- **Level:** alta

---

## Test Cases: Fuzzy Matching

### Test 4: Typo Detection (>70%)

**Input:**
```json
{
  "nombre": "José",
  "apellido": "Gonzales"
}
```

**Should Match:**
- José González (typo in apellido)
- Jose Gonsalez (double typo)

**Expected Confidence:**
- "José González" → **~95%** (one character difference) → **alta**
- "Jose Gonsalez" → **~90%** (minor typo) → **alta**

---

### Test 5: Word Order (Token Sort)

**Input:**
```json
{
  "nombre": "García",
  "apellido": "Juan"
}
```

**Should Match:**
- Juan García (reversed order)

**Expected Confidence:**
- **100%** (token_sort_ratio handles word order) → **alta**

---

### Test 6: Second Surname (Puerto Rico Format)

**Input:**
```json
{
  "nombre": "José",
  "apellido": "García",
  "segundo_apellido": "Rivera"
}
```

**Should Match:**
- José García Rivera (full match)
- Jose Garcia Rivera (no accents)
- José García (partial match, still high similarity)

**Expected Confidence:**
- Full match: **100%** → **alta**
- Partial match: **~85-90%** → **alta/media**

---

### Test 7: Company Name Fuzzy Match

**Input:**
```json
{
  "nombre_empresa": "Corporación Internacional ABC"
}
```

**Should Match:**
- Corporacion Internacional ABC (no accent)
- Corporación Int. ABC (abbreviation)
- Corporation Internacional ABC (translation)

**Expected Confidence:**
- No accent: **100%** → **alta**
- Abbreviation: **~85%** → **media**
- Translation: **~75%** → **media**

---

### Test 8: Related Parties Search

**Input:**
```json
{
  "nombre": "María",
  "apellido": "López"
}
```

**Should Find:**
- Client named "María López"
- Related party in historical matters (demandante, demandado, etc.)

**Result Fields:**
```json
{
  "tipo_coincidencia": "parte_relacionada_demandado",
  "campo_coincidente": "parte_relacionada (demandado: María López)",
  "similitud_score": 100.0,
  "nivel_confianza": "alta"
}
```

---

## Test Cases: Edge Cases

### Test 9: Minimum Threshold (70%)

**Input:**
```json
{
  "nombre": "José",
  "apellido": "García"
}
```

**Should NOT Match (Below 70%):**
- John Smith (completely different)
- María Rodríguez (different person)

**Should Match (Above 70%):**
- José Garcia (95%+)
- Jose Garsia (typo, ~85%)
- J. García (abbreviation, ~75%)

---

### Test 10: Multiple Results Ordering

**Input:**
```json
{
  "nombre": "Juan",
  "apellido": "Pérez"
}
```

**Expected Results Order:**
1. Juan Pérez - 100% (exact) - **alta**
2. Juan Perez - 100% (no accent) - **alta**
3. Juan P. - 85% (abbreviation) - **media**
4. Juan Peres - 75% (typo) - **media**

**Results should be ordered by `similitud_score` (highest first)**

---

## Manual Testing Steps

### Using cURL

1. **Create a test firm:**
```bash
curl -X POST "http://localhost:8000/api/v1/firmas/" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Bufete de Prueba PR"
  }'
```

2. **Create test clients with accents:**
```bash
# Client 1: José García Rivera
curl -X POST "http://localhost:8000/api/v1/clientes/" \
  -H "Content-Type: application/json" \
  -H "X-Firm-ID: 1" \
  -d '{
    "nombre": "José",
    "apellido": "García",
    "segundo_apellido": "Rivera"
  }'

# Client 2: María Rodríguez
curl -X POST "http://localhost:8000/api/v1/clientes/" \
  -H "Content-Type: application/json" \
  -H "X-Firm-ID: 1" \
  -d '{
    "nombre": "María",
    "apellido": "Rodríguez"
  }'

# Client 3: Juan González (no accent in DB)
curl -X POST "http://localhost:8000/api/v1/clientes/" \
  -H "Content-Type: application/json" \
  -H "X-Firm-ID: 1" \
  -d '{
    "nombre": "Juan",
    "apellido": "Gonzalez"
  }'
```

3. **Create matters for clients:**
```bash
curl -X POST "http://localhost:8000/api/v1/asuntos/" \
  -H "Content-Type: application/json" \
  -H "X-Firm-ID: 1" \
  -d '{
    "cliente_id": 1,
    "nombre_asunto": "García vs. State of PR",
    "estado": "activo"
  }'
```

4. **Add related parties:**
```bash
curl -X POST "http://localhost:8000/api/v1/partes-relacionadas/" \
  -H "Content-Type: application/json" \
  -H "X-Firm-ID: 1" \
  -d '{
    "asunto_id": 1,
    "nombre": "Pedro González Rivera",
    "tipo_relacion": "demandado"
  }'
```

5. **Test conflict search (with accent):**
```bash
curl -X POST "http://localhost:8000/api/v1/conflictos/verificar" \
  -H "Content-Type: application/json" \
  -H "X-Firm-ID: 1" \
  -d '{
    "nombre": "José",
    "apellido": "García"
  }'
```

6. **Test conflict search (without accent - should match):**
```bash
curl -X POST "http://localhost:8000/api/v1/conflictos/verificar" \
  -H "Content-Type: application/json" \
  -H "X-Firm-ID: 1" \
  -d '{
    "nombre": "Jose",
    "apellido": "Garcia"
  }'
```

---

## Using API Documentation (Swagger UI)

1. Navigate to: `http://localhost:8000/api/v1/docs`
2. Click on **POST /api/v1/conflictos/verificar**
3. Click "Try it out"
4. Add header: `X-Firm-ID: 1`
5. Enter request body:
```json
{
  "nombre": "José",
  "apellido": "González"
}
```
6. Click "Execute"
7. Verify response includes confidence scores

---

## Expected Response Format

```json
{
  "termino_busqueda": "José García Rivera",
  "total_conflictos": 3,
  "conflictos": [
    {
      "cliente_id": 1,
      "cliente_nombre": "José García Rivera",
      "asunto_id": 1,
      "asunto_nombre": "García vs. State of PR",
      "estado_asunto": "activo",
      "tipo_coincidencia": "cliente_persona",
      "similitud_score": 100.0,
      "nivel_confianza": "alta",
      "campo_coincidente": "cliente_nombre"
    },
    {
      "cliente_id": 2,
      "cliente_nombre": "Juan González Pérez",
      "asunto_id": 3,
      "asunto_nombre": "González vs. Municipality",
      "estado_asunto": "cerrado",
      "tipo_coincidencia": "parte_relacionada_demandado",
      "similitud_score": 85.5,
      "nivel_confianza": "media",
      "campo_coincidente": "parte_relacionada (demandado: José García)"
    },
    {
      "cliente_id": 5,
      "cliente_nombre": "María López Torres",
      "asunto_id": 7,
      "asunto_nombre": "López vs. Insurance Co.",
      "estado_asunto": "activo",
      "tipo_coincidencia": "parte_relacionada_conyuge",
      "similitud_score": 72.3,
      "nivel_confianza": "media",
      "campo_coincidente": "parte_relacionada (conyuge: José García R.)"
    }
  ],
  "mensaje": "Se encontraron 3 posible(s) conflicto(s): 1 alta confianza, 2 media confianza"
}
```

---

## Verification Checklist

- [ ] José matches Jose (100% confidence)
- [ ] María matches Maria (100% confidence)
- [ ] González matches Gonzalez (100% confidence)
- [ ] Searches in both clients and related parties
- [ ] Results ordered by similarity score (highest first)
- [ ] Confidence levels correctly assigned (alta ≥90%, media 70-89%)
- [ ] Match context shows which field matched
- [ ] Searches across ALL matter statuses (activo, cerrado, pendiente, archivado)
- [ ] Handles segundo_apellido correctly
- [ ] Company names normalize accents
- [ ] Fuzzy matching catches typos (>70% threshold)
- [ ] Word order variations work (García Juan = Juan García)

---

## Performance Notes

- Fuzzy matching is done in-memory (after DB query)
- For large databases (>10,000 clients), consider:
  - Database-level fuzzy matching (pg_trgm extension)
  - Caching frequent searches
  - Indexing normalized names

---

## Troubleshooting

### Issue: Accent matches not working
**Check:** Verify `unidecode` is installed: `pip list | grep unidecode`

### Issue: Low confidence scores
**Check:** Verify `FUZZY_THRESHOLD` in `.env` is set to 70 (default)

### Issue: No results found
**Check:**
1. Verify firm_id is correct
2. Check that clients/parties are active (`esta_activo=True`)
3. Verify matters exist for clients
4. Check threshold settings

### Issue: Related parties not searched
**Check:** Verify related parties are associated with active matters

---

## Next Steps

After verifying all test cases:

1. Run automated tests (if available)
2. Test with production-like data volume
3. Monitor performance with >1000 clients
4. Consider adding synonym dictionary for common variations
5. Add logging for confidence score distribution analysis
