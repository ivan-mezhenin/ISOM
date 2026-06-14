#include "isom.h"
#include <ctype.h>

void copy_string(char* destination, const char* source) {
    strncpy(destination, source, MAX_NAME - 1);
    destination[MAX_NAME - 1] = '\0';
}

bool is_variable(const char* string) {
    return string && string[0] == 'x';
}

// --- Dynamic hash table for O(1) dedup ---

typedef struct {
    char key[MAX_NAME];
    int val;
    bool occupied;
} HashEntry;

typedef struct {
    HashEntry* entries;
    int capacity;
    int count;
} HashTable;

static unsigned long ht_hash(const char* str) {
    unsigned long h = 14695981039346656037UL;
    for (; *str; str++) {
        h ^= (unsigned char)*str;
        h *= 1099511628211UL;
    }
    return h;
}

static HashTable* ht_create(int hint) {
    HashTable* ht = (HashTable*)malloc(sizeof(HashTable));
    if (!ht) return NULL;
    int cap = 16;
    while (cap < hint) cap *= 2;
    ht->entries = (HashEntry*)calloc(cap, sizeof(HashEntry));
    if (!ht->entries) { free(ht); return NULL; }
    ht->capacity = cap;
    ht->count = 0;
    return ht;
}

static void ht_destroy(HashTable* ht) {
    if (ht) {
        free(ht->entries);
        free(ht);
    }
}

static int ht_find(HashTable* ht, const char* key) {
    unsigned long h = ht_hash(key) & (unsigned long)(ht->capacity - 1);
    while (ht->entries[h].occupied && strcmp(ht->entries[h].key, key) != 0)
        h = (h + 1) & (unsigned long)(ht->capacity - 1);
    if (ht->entries[h].occupied)
        return ht->entries[h].val;
    return -1;
}

static void ht_expand(HashTable* ht) {
    int new_cap = ht->capacity * 2;
    HashEntry* new_entries = (HashEntry*)calloc(new_cap, sizeof(HashEntry));
    if (!new_entries) return;
    for (int i = 0; i < ht->capacity; i++) {
        if (ht->entries[i].occupied) {
            unsigned long h = ht_hash(ht->entries[i].key) & (unsigned long)(new_cap - 1);
            while (new_entries[h].occupied)
                h = (h + 1) & (unsigned long)(new_cap - 1);
            copy_string(new_entries[h].key, ht->entries[i].key);
            new_entries[h].val = ht->entries[i].val;
            new_entries[h].occupied = true;
        }
    }
    free(ht->entries);
    ht->entries = new_entries;
    ht->capacity = new_cap;
}

static void ht_insert(HashTable* ht, const char* key, int val) {
    if (ht->count * 2 >= ht->capacity) {
        ht_expand(ht);
    }
    unsigned long h = ht_hash(key) & (unsigned long)(ht->capacity - 1);
    while (ht->entries[h].occupied && strcmp(ht->entries[h].key, key) != 0)
        h = (h + 1) & (unsigned long)(ht->capacity - 1);
    if (!ht->entries[h].occupied) {
        ht->count++;
    }
    copy_string(ht->entries[h].key, key);
    ht->entries[h].val = val;
    ht->entries[h].occupied = true;
}

Unifier* unifier_alloc(void) {
    Unifier* unifier = (Unifier*)calloc(1, sizeof(Unifier));
    if (!unifier) {
        return NULL;
    }

    unifier->subs = (Sub*)calloc(MAX_UNIQUE, sizeof(Sub));
    if (!unifier->subs) {
        free(unifier);
        return NULL;
    }

    unifier->count = 0;
    unifier->capacity = MAX_UNIQUE;
    return unifier;
}

void unifier_init(Unifier* unifier) {
    unifier->subs = (Sub*)calloc(MAX_UNIQUE, sizeof(Sub));
    unifier->count = 0;
    unifier->capacity = MAX_UNIQUE;
}

void unifier_clear(Unifier* unifier) {
    if (unifier->subs) {
        free(unifier->subs);
        unifier->subs = NULL;
    }
}

void unifier_free(Unifier* unifier) {
    if (!unifier) {
        return;
    }
    
    if (unifier->subs) {
        free(unifier->subs);
    }

    free(unifier);
}

void print_unifier(Unifier* unifier) {
    if (!unifier || unifier->count == 0) {
        printf("  (none)\n");
        return;
    }

    for (int i = 0; i < unifier->count; i++) {
        printf("  %s -> %s\n", unifier->subs[i].from, unifier->subs[i].to);
    }
}

// --- Parsing ---
Hypergraph* parse_hypergraph(const char* string) {
    Hypergraph* graph = (Hypergraph*)calloc(1, sizeof(Hypergraph));
    if (!graph) return NULL;
    graph->edges = (Hyperedge*)calloc(EDGE_INIT_CAPACITY, sizeof(Hyperedge));
    if (!graph->edges) { free(graph); return NULL; }
    graph->edge_capacity = EDGE_INIT_CAPACITY;
    graph->edge_count = 0;
    graph->max_arity = 0;

    const char* ptr = string;

    while (*ptr) {
        while (*ptr == ' ') {
            ptr++;
        }

        if (!*ptr || *ptr == '&') {
            if (*ptr == '&') ptr++;
            continue;
        }

        const char* pred_start = ptr;
        while (*ptr && *ptr != '(') {
            ptr++;
        }

        if (!*ptr) {
            break;
        }

        // Grow edges array if needed
        if (graph->edge_count >= graph->edge_capacity) {
            int new_cap = graph->edge_capacity * 2;
            Hyperedge* new_edges = (Hyperedge*)realloc(graph->edges, new_cap * sizeof(Hyperedge));
            if (!new_edges) { free_hypergraph(graph); return NULL; }
            graph->edges = new_edges;
            graph->edge_capacity = new_cap;
        }

        Hyperedge* edge = &graph->edges[graph->edge_count];
        int pred_len = ptr - pred_start;
        if (pred_len >= MAX_NAME) {
            pred_len = MAX_NAME - 1;
        }

        strncpy(edge->pred, pred_start, pred_len);
        edge->pred[pred_len] = '\0';

        ptr++;
        const char* args_start = ptr;
        while (*ptr && *ptr != ')') {
            ptr++;
        }

        if (*ptr != ')') {
            free_hypergraph(graph);
            return NULL;
        }

        int args_len = ptr - args_start;
        char* args_str = (char*)malloc(args_len + 1);
        if (!args_str) { free_hypergraph(graph); return NULL; }
        strncpy(args_str, args_start, args_len);
        args_str[args_len] = '\0';

        edge->arity = 0;
        char* token = strtok(args_str, ",");
        while (token && edge->arity < MAX_ARGS) {
            copy_string(edge->args[edge->arity], token);
            edge->arity++;
            token = strtok(NULL, ",");
        }
        free(args_str);

        if (edge->arity > graph->max_arity) {
            graph->max_arity = edge->arity;
        }
        graph->edge_count++;
        ptr++;

        while (*ptr == ' ') {
            ptr++;
        }

        if (*ptr == '&') {
            ptr++;
        } else if (*ptr) {
            break;
        }
    }
    
    return graph;
}

void free_hypergraph(Hypergraph* graph) {
    if (graph) {
        free(graph->edges);
        free(graph);
    }
}

void print_hypergraph(Hypergraph* graph) {
    if (!graph) {
        return;
    }

    for (int i = 0; i < graph->edge_count; i++) {
        Hyperedge* edge = &graph->edges[i];
        printf("%s(", edge->pred);
        for (int j = 0; j < edge->arity; j++) {
            printf("%s", edge->args[j]);
            if (j < edge->arity - 1) {
                printf(",");
            }
        }
        printf(") ");
    }

    printf("\n");
}

// --- Characteristics ---
typedef struct {
    char name[MAX_NAME];
    int vector[MAX_ARGS];
} ArgCharacteristic;

typedef struct {
    ArgCharacteristic* items;
    int count;
    int arity;
    HashTable* ht;
} GraphCharacteristics;

GraphCharacteristics* calculate_characteristics(Hypergraph* graph) {
    int hint = graph->edge_count * 4;
    if (hint < 1024) hint = 1024;
    HashTable* ht = ht_create(hint);
    if (!ht) return NULL;

    int unique_count = 0;
    for (int i = 0; i < graph->edge_count; i++) {
        for (int j = 0; j < graph->edges[i].arity; j++) {
            if (ht_find(ht, graph->edges[i].args[j]) == -1) {
                ht_insert(ht, graph->edges[i].args[j], unique_count);
                unique_count++;
            }
        }
    }

    GraphCharacteristics* graph_char = (GraphCharacteristics*)malloc(sizeof(GraphCharacteristics));
    if (!graph_char) { ht_destroy(ht); return NULL; }
    graph_char->count = unique_count;
    graph_char->arity = graph->max_arity;
    graph_char->items = (ArgCharacteristic*)calloc(unique_count, sizeof(ArgCharacteristic));
    if (!graph_char->items) { ht_destroy(ht); free(graph_char); return NULL; }

    for (int i = 0; i < ht->capacity; i++) {
        if (ht->entries[i].occupied) {
            copy_string(graph_char->items[ht->entries[i].val].name, ht->entries[i].key);
        }
    }

    for (int edge_i = 0; edge_i < graph->edge_count; edge_i++) {
        for (int a = 0; a < graph->edges[edge_i].arity; a++) {
            int idx = ht_find(ht, graph->edges[edge_i].args[a]);
            if (idx >= 0 && idx < graph_char->count) {
                graph_char->items[idx].vector[a]++;
            }
        }
    }

    graph_char->ht = ht;
    return graph_char;
}

void free_characteristics(GraphCharacteristics* graph_char) {
    if (graph_char) {
        if (graph_char->items) {
            free(graph_char->items);
        }
        if (graph_char->ht) {
            ht_destroy(graph_char->ht);
        }
        free(graph_char);
    }
}

int compare_arg_characteristic(void* ctx, const void* a, const void* b) {
    int arity = *(int*)ctx;
    ArgCharacteristic* arg_char1 = (ArgCharacteristic*)a;
    ArgCharacteristic* arg_char2 = (ArgCharacteristic*)b;

    for (int i = 0; i < arity; i++) {
        if (arg_char1->vector[i] < arg_char2->vector[i]) {
            return -1;
        }
        if (arg_char1->vector[i] > arg_char2->vector[i]) {
            return 1;
        }
    }

    return strcmp(arg_char1->name, arg_char2->name);
}

void sort_characteristics(GraphCharacteristics* graph_char) {
    qsort_r(graph_char->items, graph_char->count, sizeof(ArgCharacteristic),
            &graph_char->arity, compare_arg_characteristic);
}

bool compare_characteristics(GraphCharacteristics* chars1, GraphCharacteristics* chars2) {
    if (chars1->count != chars2->count || chars1->arity != chars2->arity) {
        return false;
    }

    sort_characteristics(chars1);
    sort_characteristics(chars2);
    for (int i = 0; i < chars1->count; i++) {
        for (int j = 0; j < chars1->arity; j++) {
            if (chars1->items[i].vector[j] != chars2->items[i].vector[j]) {
                return false;
            }
        }
    }

    return true;
}

// --- Constants and variables ---
int get_constants(Hypergraph* graph, char result[][MAX_NAME]) {
    HashTable* ht = ht_create(1024);
    if (!ht) return 0;

    int count = 0;
    for (int i = 0; i < graph->edge_count && count < MAX_UNIQUE; i++) {
        for (int j = 0; j < graph->edges[i].arity; j++) {
            if (!is_variable(graph->edges[i].args[j]) && ht_find(ht, graph->edges[i].args[j]) == -1) {
                copy_string(result[count], graph->edges[i].args[j]);
                ht_insert(ht, graph->edges[i].args[j], count);
                count++;
            }
        }
    }

    ht_destroy(ht);
    return count;
}

int get_variables(Hypergraph* graph, char result[][MAX_NAME]) {
    HashTable* ht = ht_create(1024);
    if (!ht) return 0;

    int count = 0;
    for (int i = 0; i < graph->edge_count && count < MAX_UNIQUE; i++) {
        for (int j = 0; j < graph->edges[i].arity; j++) {
            if (is_variable(graph->edges[i].args[j]) && ht_find(ht, graph->edges[i].args[j]) == -1) {
                copy_string(result[count], graph->edges[i].args[j]);
                ht_insert(ht, graph->edges[i].args[j], count);
                count++;
            }
        }
    }

    ht_destroy(ht);
    return count;
}

// Build template H from G1, returns lambda1: const_G1 -> x_i
Hypergraph* build_template(Hypergraph* graph1, Unifier* lambda1) {
    Hypergraph* template_graph = (Hypergraph*)calloc(1, sizeof(Hypergraph));
    if (!template_graph) return NULL;
    template_graph->edge_count = graph1->edge_count;
    template_graph->edge_capacity = graph1->edge_count;
    template_graph->max_arity = graph1->max_arity;
    template_graph->edges = (Hyperedge*)calloc(graph1->edge_count, sizeof(Hyperedge));
    if (!template_graph->edges) { free(template_graph); return NULL; }
    lambda1->count = 0;

    char (*consts)[MAX_NAME] = (char(*)[MAX_NAME])calloc(MAX_UNIQUE, MAX_NAME);
    if (!consts) {
        return NULL;
    }

    int const_count = get_constants(graph1, consts);

    for (int i = 0; i < const_count; i++) {
        char var_name[MAX_NAME];
        snprintf(var_name, sizeof(var_name), "x%d", i + 1);
        copy_string(lambda1->subs[i].from, consts[i]);
        copy_string(lambda1->subs[i].to, var_name);
        lambda1->count++;
    }

    // Build hash table from lambda1 for O(1) lookup
    HashTable* lambda1_ht = ht_create(lambda1->count);
    if (!lambda1_ht) { free(consts); free(template_graph); return NULL; }
    for (int k = 0; k < lambda1->count; k++) {
        ht_insert(lambda1_ht, lambda1->subs[k].from, k);
    }

    // Build H: replace constants with their x_i, keep variables as-is
    for (int i = 0; i < graph1->edge_count; i++) {
        copy_string(template_graph->edges[i].pred, graph1->edges[i].pred);
        template_graph->edges[i].arity = graph1->edges[i].arity;
        for (int j = 0; j < graph1->edges[i].arity; j++) {
            char* arg = graph1->edges[i].args[j];
            if (is_variable(arg)) {
                copy_string(template_graph->edges[i].args[j], arg);
            } 
            else {
                int idx = ht_find(lambda1_ht, arg);
                if (idx >= 0) {
                    copy_string(template_graph->edges[i].args[j], lambda1->subs[idx].to);
                }
            }
        }
    }

    ht_destroy(lambda1_ht);

    free(consts);
    return template_graph;
}

Hypergraph* apply_unifier(Hypergraph* graph, Unifier* unifier) {
    Hypergraph* result = (Hypergraph*)calloc(1, sizeof(Hypergraph));
    if (!result) return NULL;
    result->edge_count = graph->edge_count;
    result->edge_capacity = graph->edge_count;
    result->max_arity = graph->max_arity;
    result->edges = (Hyperedge*)calloc(graph->edge_count, sizeof(Hyperedge));
    if (!result->edges) { free(result); return NULL; }

    HashTable* ht = ht_create(unifier->count);
    if (!ht) {
        free_hypergraph(result);
        return NULL;
    }
    for (int k = 0; k < unifier->count; k++) {
        ht_insert(ht, unifier->subs[k].from, k);
    }

    for (int i = 0; i < graph->edge_count; i++) {
        copy_string(result->edges[i].pred, graph->edges[i].pred);
        result->edges[i].arity = graph->edges[i].arity;
        for (int j = 0; j < graph->edges[i].arity; j++) {
            int idx = ht_find(ht, graph->edges[i].args[j]);
            if (idx >= 0) {
                copy_string(result->edges[i].args[j], unifier->subs[idx].to);
            } else {
                copy_string(result->edges[i].args[j], graph->edges[i].args[j]);
            }
        }
    }

    ht_destroy(ht);
    return result;
}

// Compose u1 and u2: apply u2 to values of u1
Unifier* compose_unifiers(Unifier* unifier1, Unifier* unifier2) {
    Unifier* result = unifier_alloc();
    if (!result) {
        return NULL;
    }

    if (unifier2->count == 0) {
        for (int i = 0; i < unifier1->count && result->count < MAX_UNIQUE; i++) {
            copy_string(result->subs[result->count].from, unifier1->subs[i].from);
            copy_string(result->subs[result->count].to, unifier1->subs[i].to);
            result->count++;
        }
        return result;
    }

    HashTable* ht = ht_create(unifier2->count);
    if (!ht) {
        unifier_free(result);
        return NULL;
    }
    for (int j = 0; j < unifier2->count; j++) {
        ht_insert(ht, unifier2->subs[j].from, j);
    }

    for (int i = 0; i < unifier1->count && result->count < MAX_UNIQUE; i++) {
        copy_string(result->subs[result->count].from, unifier1->subs[i].from);
        char from_value[MAX_NAME] = {0};
        copy_string(from_value, unifier1->subs[i].to);
        int idx = ht_find(ht, from_value);
        if (idx >= 0) {
            copy_string(from_value, unifier2->subs[idx].to);
        }
        copy_string(result->subs[result->count].to, from_value);
        result->count++;
    }

    ht_destroy(ht);
    return result;
}

// --- Isomorphism checks ---
bool is_literal_isomorphic(char args1[][MAX_NAME], char args2[][MAX_NAME], int arity) {
    int count1 = 0, count2 = 0;

    for (int i = 0; i < arity; i++) {
        int id1 = -1;
        for (int j = 0; j < count1; j++) {
            if (strcmp(args1[i], args1[j]) == 0) {
                id1 = j;
                break;
            }
        }

        if (id1 == -1) {
            id1 = count1;
            count1++;
        }

        int id2 = -1;
        for (int j = 0; j < count2; j++) {
            if (strcmp(args2[i], args2[j]) == 0) {
                id2 = j;
                break;
            }
        }

        if (id2 == -1) {
            id2 = count2;
            count2++;
        }

        if (id1 != id2) {
            return false;
        }
    }

    return true;
}

bool edge_is_isomorphic(Hyperedge* edge1, Hyperedge* edge2) {
    if (edge1->arity != edge2->arity) {
        return false;
    }

    if (strcmp(edge1->pred, edge2->pred) != 0) {
        return false;
    }

    return is_literal_isomorphic(edge1->args, edge2->args, edge1->arity);
}

// --- Edge comparison for qsort ---
static int edge_compare(void* ctx, const void* a, const void* b) {
    Hyperedge* edges = (Hyperedge*)ctx;
    int ia = *(const int*)a;
    int ib = *(const int*)b;
    int d = strcmp(edges[ia].pred, edges[ib].pred);
    if (d) return d;
    if (edges[ia].arity != edges[ib].arity) return edges[ia].arity - edges[ib].arity;
    for (int i = 0; i < edges[ia].arity; i++) {
        d = strcmp(edges[ia].args[i], edges[ib].args[i]);
        if (d) return d;
    }
    return 0;
}

bool hypergraph_is_isomorphic(Hypergraph* graph1, Hypergraph* graph2) {
    if (graph1->edge_count != graph2->edge_count) {
        return false;
    }

    int n = graph1->edge_count;
    if (n < 50) {
        bool* used = (bool*)calloc(n, sizeof(bool));
        if (!used) return false;
        for (int i = 0; i < n; i++) {
            bool found = false;
            for (int j = 0; j < n; j++) {
                if (!used[j] && edge_is_isomorphic(&graph1->edges[i], &graph2->edges[j])) {
                    used[j] = true;
                    found = true;
                    break;
                }
            }
            if (!found) {
                free(used);
                return false;
            }
        }
        free(used);
        return true;
    }

    int* idx1 = (int*)malloc(n * sizeof(int));
    int* idx2 = (int*)malloc(n * sizeof(int));
    if (!idx1 || !idx2) {
        free(idx1); free(idx2);
        return false;
    }
    for (int i = 0; i < n; i++) {
        idx1[i] = i;
        idx2[i] = i;
    }

    qsort_r(idx1, n, sizeof(int), graph1->edges, edge_compare);
    qsort_r(idx2, n, sizeof(int), graph2->edges, edge_compare);

    bool ok = true;
    for (int i = 0; i < n; i++) {
        if (!edge_is_isomorphic(&graph1->edges[idx1[i]], &graph2->edges[idx2[i]])) {
            ok = false;
            break;
        }
    }

    free(idx1);
    free(idx2);
    return ok;
}

// --- Characteristic-based pruning for lambda2 search ---
// --- Find lambda2 (stop at first) - iterative backtrack ---
static bool vectors_equal(int* v1, int* v2, int n) {
    for (int i = 0; i < n; i++) {
        if (v1[i] != v2[i]) return false;
    }
    return true;
}

bool search_lambda2(Hypergraph* template_graph, Hypergraph* graph2,
                    Unifier* current,
                    char variables[][MAX_NAME], int var_count,
                    char constants[][MAX_NAME], int const_count,
                    bool used_constants[],
                    int* var_group, int* group_next, int* group_head, int* group_tail,
                    int* assigned_const) {
    if (var_count == 0) {
        Hypergraph* applied_template = apply_unifier(template_graph, current);
        bool ok = applied_template && hypergraph_is_isomorphic(applied_template, graph2);
        if (applied_template) free_hypergraph(applied_template);
        return ok;
    }

    int depth = 0;
    while (depth >= 0) {
        if (depth == var_count) {
            Hypergraph* applied_template = apply_unifier(template_graph, current);
            bool ok = applied_template && hypergraph_is_isomorphic(applied_template, graph2);
            if (applied_template) free_hypergraph(applied_template);
            if (ok) return true;

            depth--;
            while (depth >= 0) {
                int g = var_group[depth];
                int ci = assigned_const[depth];
                used_constants[ci] = false;
                current->count--;

                group_next[ci] = -1;
                if (group_tail[g] >= 0) {
                    group_next[group_tail[g]] = ci;
                } else {
                    group_head[g] = ci;
                }
                group_tail[g] = ci;

                int next_ci = group_head[g];
                if (next_ci >= 0 && next_ci != ci) {
                    group_head[g] = group_next[next_ci];
                    if (group_head[g] < 0) group_tail[g] = -1;
                    copy_string(current->subs[current->count].from, variables[depth]);
                    copy_string(current->subs[current->count].to, constants[next_ci]);
                    current->count++;
                    used_constants[next_ci] = true;
                    assigned_const[depth] = next_ci;
                    depth++;
                    break;
                }
                depth--;
            }
            continue;
        }

        int g = var_group[depth];
        int ci = group_head[g];
        if (ci >= 0) {
            group_head[g] = group_next[ci];
            if (group_head[g] < 0) group_tail[g] = -1;
            copy_string(current->subs[current->count].from, variables[depth]);
            copy_string(current->subs[current->count].to, constants[ci]);
            current->count++;
            used_constants[ci] = true;
            assigned_const[depth] = ci;
            depth++;
            continue;
        }

        depth--;
        while (depth >= 0) {
            int g = var_group[depth];
            int ci = assigned_const[depth];
            used_constants[ci] = false;
            current->count--;

            group_next[ci] = -1;
            if (group_tail[g] >= 0) {
                group_next[group_tail[g]] = ci;
            } else {
                group_head[g] = ci;
            }
            group_tail[g] = ci;

            int next_ci = group_head[g];
            if (next_ci >= 0 && next_ci != ci) {
                group_head[g] = group_next[next_ci];
                if (group_head[g] < 0) group_tail[g] = -1;
                copy_string(current->subs[current->count].from, variables[depth]);
                copy_string(current->subs[current->count].to, constants[next_ci]);
                current->count++;
                used_constants[next_ci] = true;
                assigned_const[depth] = next_ci;
                depth++;
                break;
            }
            depth--;
        }
    }

    return false;
}

// Get ALL unique arguments (variables and constants) from a hypergraph
int get_all_arguments(Hypergraph* graph, char result[][MAX_NAME]) {
    int hint = graph->edge_count * 4;
    if (hint < 1024) hint = 1024;
    HashTable* ht = ht_create(hint);
    if (!ht) return 0;

    int count = 0;
    for (int i = 0; i < graph->edge_count && count < MAX_UNIQUE; i++) {
        for (int j = 0; j < graph->edges[i].arity; j++) {
            if (ht_find(ht, graph->edges[i].args[j]) == -1) {
                copy_string(result[count], graph->edges[i].args[j]);
                ht_insert(ht, graph->edges[i].args[j], count);
                count++;
            }
        }
    }

    ht_destroy(ht);
    return count;
}

// --- Main function: returns unifier or NULL ---
Unifier* check_isomorphism(Hypergraph* graph1, Hypergraph* graph2) {
    GraphCharacteristics* chars1 = NULL;
    GraphCharacteristics* chars2 = NULL;
    Hypergraph* template_graph = NULL;
    char (*variables)[MAX_NAME] = NULL;
    char (*all_arguments)[MAX_NAME] = NULL;
    bool* used_arguments = NULL;
    Unifier lambda1 = {0};
    Unifier lambda2 = {0};
    Unifier* result = NULL;
    int var_count = 0;
    int all_count = 0;
    int* var_group = NULL;
    int* const_group = NULL;
    int* group_sizes = NULL;
    int* char1_to_group = NULL;
    int* char2_to_group = NULL;
    HashTable* lambda1_ht = NULL;
    int group_count = 0;

    chars1 = calculate_characteristics(graph1);
    chars2 = calculate_characteristics(graph2);
    if (!chars1 || !chars2) {
        goto cleanup;
    }
    if (!compare_characteristics(chars1, chars2)) {
        goto cleanup;
    }

    unifier_init(&lambda1);
    template_graph = build_template(graph1, &lambda1);
    if (!template_graph) {
        goto cleanup;
    }

    variables = (char(*)[MAX_NAME])calloc(MAX_UNIQUE, MAX_NAME);
    if (!variables) {
        goto cleanup;
    }
    var_count = get_variables(template_graph, variables);

    all_arguments = (char(*)[MAX_NAME])calloc(MAX_UNIQUE, MAX_NAME);
    if (!all_arguments) {
        goto cleanup;
    }
    all_count = get_all_arguments(graph2, all_arguments);

    // Build groups by characteristic vector for O(1) search

    lambda1_ht = ht_create(lambda1.count);
    if (!lambda1_ht) goto cleanup;
    for (int i = 0; i < lambda1.count; i++) {
        ht_insert(lambda1_ht, lambda1.subs[i].to, i);
    }

    // Assign group IDs to chars1 items (sorted by vector)
    char1_to_group = (int*)calloc(chars1->count, sizeof(int));
    if (!char1_to_group) goto cleanup;
    group_count = 1;
    char1_to_group[0] = 0;
    for (int i = 1; i < chars1->count; i++) {
        if (vectors_equal(chars1->items[i-1].vector, chars1->items[i].vector, chars1->arity)) {
            char1_to_group[i] = char1_to_group[i-1];
        } else {
            char1_to_group[i] = group_count++;
        }
    }

    // Assign groups to variables
    var_group = (int*)calloc(var_count, sizeof(int));
    if (!var_group) goto cleanup;
    for (int i = 0; i < var_count; i++) {
        int ci = -1;
        int li = ht_find(lambda1_ht, variables[i]);
        if (li >= 0) {
            ci = ht_find(chars1->ht, lambda1.subs[li].from);
        }
        if (ci < 0) {
            ci = ht_find(chars1->ht, variables[i]);
        }
        var_group[i] = (ci >= 0 && ci < chars1->count) ? char1_to_group[ci] : 0;
    }

    // Assign group IDs to chars2 items
    char2_to_group = (int*)calloc(chars2->count, sizeof(int));
    if (!char2_to_group) goto cleanup;
    char2_to_group[0] = 0;
    for (int i = 1; i < chars2->count; i++) {
        if (vectors_equal(chars2->items[i-1].vector, chars2->items[i].vector, chars2->arity)) {
            char2_to_group[i] = char2_to_group[i-1];
        } else {
            char2_to_group[i] = char2_to_group[i-1] + 1;
        }
    }

    // Assign groups to constants
    const_group = (int*)calloc(all_count, sizeof(int));
    if (!const_group) goto cleanup;
    for (int i = 0; i < all_count; i++) {
        int ci = ht_find(chars2->ht, all_arguments[i]);
        const_group[i] = (ci >= 0 && ci < chars2->count) ? char2_to_group[ci] : 0;
    }

    // Count constants per group
    group_sizes = (int*)calloc(group_count, sizeof(int));
    if (!group_sizes) goto cleanup;
    for (int i = 0; i < all_count; i++) {
        if (const_group[i] >= 0 && const_group[i] < group_count) {
            group_sizes[const_group[i]]++;
        }
    }

    // Quick check: group sizes match
    int* var_count_per_group = (int*)calloc(group_count, sizeof(int));
    if (!var_count_per_group) goto cleanup;
    for (int i = 0; i < var_count; i++) {
        if (var_group[i] >= 0 && var_group[i] < group_count) {
            var_count_per_group[var_group[i]]++;
        }
    }
    bool groups_match = true;
    for (int g = 0; g < group_count; g++) {
        if (var_count_per_group[g] != group_sizes[g]) {
            groups_match = false;
            break;
        }
    }
    free(var_count_per_group);
    if (!groups_match) goto cleanup;

    // Build linked list per group (head→c1→c2→...→cn→-1, tail=cn)
    int* group_head = (int*)calloc(group_count, sizeof(int));
    int* group_tail = (int*)calloc(group_count, sizeof(int));
    int* group_next = (int*)malloc(all_count * sizeof(int));
    if (!group_head || !group_tail || !group_next) {
        free(group_head); free(group_tail); free(group_next);
        goto cleanup;
    }
    for (int g = 0; g < group_count; g++) {
        group_head[g] = -1;
        group_tail[g] = -1;
    }
    for (int i = 0; i < all_count; i++) {
        int g = const_group[i];
        group_next[i] = -1;
        if (group_tail[g] >= 0) {
            group_next[group_tail[g]] = i;
        } else {
            group_head[g] = i;
        }
        group_tail[g] = i;
    }

    // Track which constant is assigned at each depth
    int* assigned_const = (int*)calloc(var_count, sizeof(int));
    if (!assigned_const) { free(group_head); free(group_tail); free(group_next); goto cleanup; }

    unifier_init(&lambda2);
    used_arguments = (bool*)calloc(MAX_UNIQUE, sizeof(bool));
    if (!used_arguments) {
        free(group_head); free(group_tail); free(group_next); free(assigned_const);
        goto cleanup;
    }

    if (!search_lambda2(template_graph, graph2, &lambda2, variables, var_count,
                        all_arguments, all_count, used_arguments,
                        var_group, group_next, group_head, group_tail, assigned_const)) {
        free(group_head); free(group_tail); free(group_next); free(assigned_const);
        goto cleanup;
    }

    free(group_head);
    free(group_tail);
    free(group_next);
    free(assigned_const);

    result = compose_unifiers(&lambda1, &lambda2);

cleanup:
    if (lambda1_ht) ht_destroy(lambda1_ht);
    free(char1_to_group);
    free(char2_to_group);
    free(var_group);
    free(const_group);
    free(group_sizes);
    free(variables);
    free(all_arguments);
    free(used_arguments);
    if (lambda1.subs) {
        unifier_clear(&lambda1);
    }
    if (lambda2.subs) {
        unifier_clear(&lambda2);
    }
    free_hypergraph(template_graph);
    free_characteristics(chars1);
    free_characteristics(chars2);
    return result;
}
