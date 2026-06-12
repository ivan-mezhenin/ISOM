#include "isom.h"
#include <ctype.h>

void copy_string(char* destination, const char* source) {
    strncpy(destination, source, MAX_NAME - 1);
    destination[MAX_NAME - 1] = '\0';
}

bool is_variable(const char* string) {
    return string && string[0] == 'x';
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
    const char* ptr = string;

    while (*ptr && graph->edge_count < MAX_EDGES) {
        while (*ptr == ' ') {
            ptr++;
        }

        const char* pred_start = ptr;
        while (*ptr && *ptr != '(') {
            ptr++;
        }

        if (!*ptr) {
            break;
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
            free(graph);
            return NULL;
        }

        char args_str[1024] = {0};
        strncpy(args_str, args_start, ptr - args_start);

        edge->arity = 0;
        char* token = strtok(args_str, ",");
        while (token && edge->arity < MAX_ARGS) {
            copy_string(edge->args[edge->arity], token);
            edge->arity++;
            token = strtok(NULL, ",");
        }

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
        } 

        else {
            break;
        }
    }
    
    return graph;
}

void free_hypergraph(Hypergraph* graph) {
    if (graph) {
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
} GraphCharacteristics;

GraphCharacteristics* calculate_characteristics(Hypergraph* graph) {
    char (*unique)[MAX_NAME] = (char(*)[MAX_NAME])calloc(MAX_UNIQUE, MAX_NAME);
    if (!unique) {
        return NULL;
    }
    int unique_count = 0;

    for (int i = 0; i < graph->edge_count; i++) {
        for (int j = 0; j < graph->edges[i].arity; j++) {
            bool found = false;
            for (int k = 0; k < unique_count; k++) {
                if (strcmp(unique[k], graph->edges[i].args[j]) == 0) {
                    found = true;
                    break;
                }
            }
            if (!found && unique_count < MAX_UNIQUE) {
                copy_string(unique[unique_count++], graph->edges[i].args[j]);
            }
        }
    }

    GraphCharacteristics* graph_char = (GraphCharacteristics*)malloc(sizeof(GraphCharacteristics));
    graph_char->count = unique_count;
    graph_char->arity = graph->max_arity;
    graph_char->items = (ArgCharacteristic*)calloc(unique_count, sizeof(ArgCharacteristic));

    for (int i = 0; i < unique_count; i++) {
        copy_string(graph_char->items[i].name, unique[i]);
        for (int j = 0; j < graph->max_arity; j++) {
            graph_char->items[i].vector[j] = 0;
        }

        for (int edge_i = 0; edge_i < graph->edge_count; edge_i++) {
            for (int a = 0; a < graph->edges[edge_i].arity; a++) {
                if (strcmp(graph->edges[edge_i].args[a], unique[i]) == 0) {
                    graph_char->items[i].vector[a]++;
                }
            }
        }
    }

    free(unique);
    return graph_char;
}

void free_characteristics(GraphCharacteristics* graph_char) {
    if (graph_char) {
        if (graph_char->items) {
            free(graph_char->items);
        }

        free(graph_char);
    }
}

int compare_arg_characteristic(const void* a, const void* b) {
    ArgCharacteristic* arg_char1 = (ArgCharacteristic*)a;
    ArgCharacteristic* arg_char2 = (ArgCharacteristic*)b;

    for (int i = 0; i < MAX_ARGS; i++) {
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
    qsort(graph_char->items, graph_char->count, sizeof(ArgCharacteristic), compare_arg_characteristic);
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
    int count = 0;
    for (int i = 0; i < graph->edge_count; i++) {
        for (int j = 0; j < graph->edges[i].arity; j++) {
            if (!is_variable(graph->edges[i].args[j])) {
                bool found = false;
                for (int k = 0; k < count; k++) {
                    if (strcmp(result[k], graph->edges[i].args[j]) == 0) {
                        found = true;
                        break;
                    }
                }

                if (!found && count < MAX_UNIQUE) {
                    copy_string(result[count++], graph->edges[i].args[j]);
                }
            }
        }
    }

    return count;
}

int get_variables(Hypergraph* graph, char result[][MAX_NAME]) {
    int count = 0;
    for (int i = 0; i < graph->edge_count; i++) {
        for (int j = 0; j < graph->edges[i].arity; j++) {
            if (is_variable(graph->edges[i].args[j])) {
                bool found = false;
                for (int k = 0; k < count; k++) {
                    if (strcmp(result[k], graph->edges[i].args[j]) == 0) {
                        found = true;
                        break;
                    }
                }

                if (!found && count < MAX_UNIQUE) {
                    copy_string(result[count++], graph->edges[i].args[j]);
                }
            }
        }
    }

    return count;
}

// Build template H from G1, returns lambda1: const_G1 -> x_i
Hypergraph* build_template(Hypergraph* graph1, Unifier* lambda1) {
    Hypergraph* template_graph = (Hypergraph*)calloc(1, sizeof(Hypergraph));
    template_graph->edge_count = graph1->edge_count;
    template_graph->max_arity = graph1->max_arity;
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
                for (int k = 0; k < lambda1->count; k++) {
                    if (strcmp(arg, lambda1->subs[k].from) == 0) {
                        copy_string(template_graph->edges[i].args[j], lambda1->subs[k].to);
                        break;
                    }
                }
            }
        }
    }

    free(consts);
    return template_graph;
}

Hypergraph* apply_unifier(Hypergraph* graph, Unifier* unifier) {
    Hypergraph* result = (Hypergraph*)calloc(1, sizeof(Hypergraph));
    result->edge_count = graph->edge_count;
    result->max_arity = graph->max_arity;

    for (int i = 0; i < graph->edge_count; i++) {
        copy_string(result->edges[i].pred, graph->edges[i].pred);
        result->edges[i].arity = graph->edges[i].arity;
        for (int j = 0; j < graph->edges[i].arity; j++) {
            bool found = false;
            for (int k = 0; k < unifier->count; k++) {
                if (strcmp(graph->edges[i].args[j], unifier->subs[k].from) == 0) {
                    copy_string(result->edges[i].args[j], unifier->subs[k].to);
                    found = true;
                    break;
                }
            }

            if (!found) {
                copy_string(result->edges[i].args[j], graph->edges[i].args[j]);
            }
        }
    }

    return result;
}

// Compose u1 and u2: apply u2 to values of u1
Unifier* compose_unifiers(Unifier* unifier1, Unifier* unifier2) {
    Unifier* result = unifier_alloc();
    if (!result) {
        return NULL;
    }

    for (int i = 0; i < unifier1->count && result->count < MAX_UNIQUE; i++) {
        copy_string(result->subs[result->count].from, unifier1->subs[i].from);
        char from_value[MAX_NAME] = {0};
        copy_string(from_value, unifier1->subs[i].to);
        for (int j = 0; j < unifier2->count; j++) {
            if (strcmp(from_value, unifier2->subs[j].from) == 0) {
                copy_string(from_value, unifier2->subs[j].to);
                break;
            }
        }

        copy_string(result->subs[result->count].to, from_value);
        result->count++;
    }

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

bool hypergraph_is_isomorphic(Hypergraph* graph1, Hypergraph* graph2) {
    if (graph1->edge_count != graph2->edge_count) {
        return false;
    }

    bool used[MAX_EDGES] = {false};
    for (int i = 0; i < graph1->edge_count; i++) {
        bool found = false;
        for (int j = 0; j < graph2->edge_count; j++) {
            if (!used[j] && edge_is_isomorphic(&graph1->edges[i], &graph2->edges[j])) {
                used[j] = true;
                found = true;
                break;
            }
        }

        if (!found) {
            return false;
        }
    }

    return true;
}

// --- Characteristic-based pruning for lambda2 search ---
static ArgCharacteristic* find_arg_characteristic(GraphCharacteristics* graph_char, const char* name) {
    for (int i = 0; i < graph_char->count; i++) {
        if (strcmp(graph_char->items[i].name, name) == 0) {
            return &graph_char->items[i];
        }
    }
    
    return NULL;
}

static ArgCharacteristic* find_var_characteristic(const char* var, GraphCharacteristics* chars1, Unifier* lambda1) {
    ArgCharacteristic* arg_char = find_arg_characteristic(chars1, var);
    if (arg_char) {
        return arg_char;
    }

    for (int i = 0; i < lambda1->count; i++) {
        if (strcmp(lambda1->subs[i].to, var) == 0) {
            return find_arg_characteristic(chars1, lambda1->subs[i].from);
        }
    }

    return NULL;
}

static bool characteristics_match(const char* var, GraphCharacteristics* chars1, Unifier* lambda1,
                                  const char* con, GraphCharacteristics* chars2) {
    ArgCharacteristic* var_char = find_var_characteristic(var, chars1, lambda1);
    ArgCharacteristic* const_char = find_arg_characteristic(chars2, con);
    if (!var_char || !const_char) {
        return true;
    }

    for (int i = 0; i < chars1->arity; i++) {
        if (var_char->vector[i] != const_char->vector[i]) {
            return false;
        }
    }

    return true;
}

// --- Find lambda2 (stop at first) - iterative backtrack ---
bool search_lambda2(Hypergraph* template_graph, Hypergraph* graph2,
                    Unifier* current,
                    char variables[][MAX_NAME], int var_count,
                    char constants[][MAX_NAME], int const_count,
                    bool used_constants[],
                    GraphCharacteristics* chars1, GraphCharacteristics* chars2, Unifier* lambda1) {
    if (var_count == 0) {
        Hypergraph* applied_template = apply_unifier(template_graph, current);
        bool ok = applied_template && hypergraph_is_isomorphic(applied_template, graph2);
        if (applied_template) {
            free_hypergraph(applied_template);
        }
        return ok;
    }

    int* pos = (int*)calloc(var_count, sizeof(int));
    if (!pos) {
        return false;
    }

    int depth = 0;
    while (depth >= 0) {
        if (depth == var_count) {
            Hypergraph* applied_template = apply_unifier(template_graph, current);
            bool ok = applied_template && hypergraph_is_isomorphic(applied_template, graph2);
            if (applied_template) {
                free_hypergraph(applied_template);
            }

            if (ok) {
                free(pos);
                return true;
            }

            depth--;
            if (depth >= 0) {
                used_constants[pos[depth]] = false;
                current->count--;
                pos[depth]++;
            }

            continue;
        }

        if (pos[depth] >= const_count) {
            pos[depth] = 0;
            depth--;
            if (depth >= 0) {
                used_constants[pos[depth]] = false;
                current->count--;
                pos[depth]++;
            }

            continue;
        }

        int i = pos[depth];
        if (used_constants[i] || !characteristics_match(variables[depth], chars1, lambda1, constants[i], chars2)) {
            pos[depth]++;
            continue;
        }

        copy_string(current->subs[current->count].from, variables[depth]);
        copy_string(current->subs[current->count].to, constants[i]);
        current->count++;
        used_constants[i] = true;
        depth++;
        if (depth < var_count) {
            pos[depth] = 0;
        }
    }

    free(pos);
    return false;
}

// Get ALL unique arguments (variables and constants) from a hypergraph
int get_all_arguments(Hypergraph* graph, char result[][MAX_NAME]) {
    int count = 0;
    for (int i = 0; i < graph->edge_count; i++) {
        for (int j = 0; j < graph->edges[i].arity; j++) {
            bool found = false;
            for (int k = 0; k < count; k++) {
                if (strcmp(result[k], graph->edges[i].args[j]) == 0) {
                    found = true;
                    break;
                }
            }

            if (!found && count < MAX_UNIQUE) {
                copy_string(result[count++], graph->edges[i].args[j]);
            }
        }
    }

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

    unifier_init(&lambda2);
    used_arguments = (bool*)calloc(MAX_UNIQUE, sizeof(bool));
    if (!used_arguments) {
        goto cleanup;
    }

    if (!search_lambda2(template_graph, graph2, &lambda2, variables, var_count,
                        all_arguments, all_count, used_arguments,
                        chars1, chars2, &lambda1)) {
        goto cleanup;
    }

    result = compose_unifiers(&lambda1, &lambda2);

cleanup:
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
