# app_monitor_streamlit.py
# Baseado em: monitor_metas_corregedorias_GUI_v2.5_final_corrigido.py
# Adaptado para Streamlit com Plotly por Gemini
# Data: 27/04/2025 (Data da adaptação)
# Versão: 3.0 (Streamlit + Plotly Snapshot)

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import io
import os
from datetime import datetime, timedelta
import logging
import traceback

# --- Configuração Inicial Streamlit e Logging ---
st.set_page_config(layout="wide", page_title="Monitor Metas Corregedorias")
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# ==================================
# Classe ConfiguracaoMetas (do script original)
# ==================================
class ConfiguracaoMetas:
    """Armazena constantes e configurações das Metas Nacionais."""
    # --- Pegar ANO_META da data selecionada? Ou fixar? Fixando por enquanto.
    ANO_META = datetime.now().year # Ajuste se necessário para 2025 fixo
    DATA_INICIO_META = datetime(ANO_META, 1, 1)
    DATA_FIM_META = datetime(ANO_META, 12, 31) # Usado como limite superior em alguns cálculos
    DATA_CORTE_META2 = datetime(ANO_META - 1, 8, 31)
    DATA_FIM_ANO_ANTERIOR = datetime(ANO_META - 1, 12, 31)
    PRAZO_DIAS_META3 = 140

    MOV_ARQUIVAMENTO_DEFINITIVO = '246'; MOV_DESARQUIVAMENTO = '893'
    MOV_DETERMINACAO_ARQUIVAMENTO_1 = '1063'; MOV_DETERMINACAO_ARQUIVAMENTO_2 = '12430'
    MOV_PEDIDO_PAUTA_VOTO = '12311'
    _MOVIMENTOS_JULGAMENTO_PASTA_193 = { # (Lista extensa omitida para brevidade - cole do original)
         '193', '218', '228', '472', '473', '230', '235', '236', '456', '454', '457', '458', '459', '460', '461', '462', '463', '464', '11374', '11375', '11376', '11377', '11378', '11379', '11380', '11381', '12256', '12298', '12325', '14848', '15245', '15249', '15250', '15251', '853', '10953', '10961', '11373', '12319', '12458', '12459', '12709', '12710', '12711', '12712', '12713', '12714', '12715', '12716', '12717', '12718', '12719', '12720', '12721', '12722', '12723', '12724', '14218', '15253', '15254', '15255', '15256', '15257', '15258', '15259', '15260', '15261', '15262', '15263', '15264', '15265', '15266', '15408', '385', '196', '198', '200', '202', '208', '210', '442', '443', '444', '445', '12032', '12041', '12475', '212', '446', '447', '448', '449', '214', '450', '451', '452', '453', '14680', '219', '220', '221', '237', '238', '239', '240', '241', '242', '455', '466', '471', '871', '901', '972', '973', '1042', '1043', '1044', '1046', '1047', '1048', '1049', '1050', '11411', '11801', '11878', '11879', '12028', '12616', '12735', '15322', '10964', '11401', '11402', '11403', '11404', '11405', '11406', '11407', '11408', '11409', '11795', '11796', '11876', '11877', '12033', '12034', '12187', '12252', '12253', '12254', '12257', '12258', '12321', '12322', '12323', '12324', '12326', '12327', '12328', '12329', '12330', '12331', '12433', '12434', '12435', '12436', '12438', '12439', '12440', '12441', '12442', '12443', '12450', '12451', '12452', '12453', '12649', '12650', '12651', '12652', '12653', '12654', '12661', '12666', '12667', '12668', '12669', '12670', '12672', '12673', '12674', '12675', '12676', '12677', '12792', '12664', '12678', '12660', '12662', '12663', '12679', '12680', '12681', '12682', '12683', '12684', '12685', '12686', '12687', '12688', '12689', '12690', '12691', '12692', '12693', '12694', '12695', '12696', '12697', '12698', '12699', '12700', '12701', '12702', '12703', '14210', '14211', '14213', '14214', '14215', '14216', '14217', '15023', '15024', '12738', '14099', '14219', '14777', '14778', '14937', '15022', '15026', '15027', '15028', '15029', '15030', '15165', '15166', '15211', '15212', '15213', '15214', '15252'
    }
    MOVIMENTOS_DECISAO = {MOV_DETERMINACAO_ARQUIVAMENTO_1, MOV_DETERMINACAO_ARQUIVAMENTO_2, MOV_PEDIDO_PAUTA_VOTO}.union(_MOVIMENTOS_JULGAMENTO_PASTA_193)
    MOVIMENTOS_BAIXA = {MOV_ARQUIVAMENTO_DEFINITIVO}
    MOVIMENTOS_TERMINAIS = MOVIMENTOS_DECISAO.union(MOVIMENTOS_BAIXA)

    _ASSUNTOS_AGR_REC = [ # (Lista extensa omitida - cole do original)
        '11336', '10894', '10225', '11952', '12589', '10010', '10187', '30000009', '30000010', '10012', '11560', '11937', '30000011', '30000012', '10013', '30000013', '10011', '30000020', '30000014', '30000015', '11951', '30000024', '11950', '10881', '11915', '11916', '30000016', '10283', '30000017', '30000018', '30000019', '10014', '11919', '15072', '10949'
    ]
    CLASSES_ASSUNTOS_RELEVANTES = { # (Cole do original)
         '200': _ASSUNTOS_AGR_REC, '1299': _ASSUNTOS_AGR_REC,
         '1262': ['__TODOS__'], '1264': ['__TODOS__'], '20000002': ['__TODOS__'],
         '1301': ['__TODOS__'], '1308': ['__TODOS__'], '11892': ['__TODOS__']
    }
    CLASSES_RELEVANTES = list(CLASSES_ASSUNTOS_RELEVANTES.keys())
    CLASSE_EXCLUIDA_NOME = "Representação por Excesso de Prazo"; CLASSE_EXCLUIDA_CODIGO = None # Ajuste se necessário

    COLUNA_ID_PROCESSO = 'id_processo_trf'; COLUNA_NR_PROCESSO = 'nr_processo'
    COLUNA_CLASSE_COD = 'cd_classe_judicial'; COLUNA_CLASSE_NOME = 'ds_classe_judicial'
    COLUNA_ASSUNTO_COD = 'cd_assunto_principal'; # COLUNA_ASSUNTO_NOME = 'ds_assunto_principal' # Não essencial na lógica
    COLUNA_DATA_AUTUACAO = 'dt_autuacao'
    COLUNA_MOVIMENTO_COD = 'codigo_movimento'; # COLUNA_MOVIMENTO_NOME = 'movimento' # Não essencial
    COLUNA_MOVIMENTO_DATA = 'lancado_em'
    COLUNA_TAREFA_ID_PROCESSO = 'id_processo_trf'; COLUNA_TAREFA_FLUXO = 'fluxo'
    COLUNA_TAREFA_NOME = 'tarefa'; COLUNA_TAREFA_INICIO = 'inicio_tarefa'; COLUNA_TAREFA_FIM = 'fim_tarefa'

    COLUNAS_ESSENCIAIS_CABECALHO = [COLUNA_ID_PROCESSO, COLUNA_NR_PROCESSO, COLUNA_CLASSE_COD, COLUNA_CLASSE_NOME, COLUNA_ASSUNTO_COD, COLUNA_DATA_AUTUACAO]
    COLUNAS_ESSENCIAIS_MOVIMENTOS = [COLUNA_ID_PROCESSO, COLUNA_MOVIMENTO_COD, COLUNA_MOVIMENTO_DATA]
    COLUNAS_ESSENCIAIS_TAREFAS = [COLUNA_TAREFA_ID_PROCESSO, COLUNA_TAREFA_FLUXO, COLUNA_TAREFA_NOME, COLUNA_TAREFA_INICIO, COLUNA_TAREFA_FIM]

# ==========================
# Classe CarregadorDados (Adaptada para Streamlit UploadedFile)
# ==========================
class CarregadorDados:
    """Carrega e prepara dados de Cabeçalhos, Movimentos e Tarefas a partir de UploadedFile."""
    def __init__(self, config=ConfiguracaoMetas, logger=None):
        self.config = config
        self.logger = logger if logger else logging.getLogger()

    def _validar_colunas(self, df, colunas_essenciais, nome_arquivo):
        # (Mesma implementação do script original)
        if df is None: return False
        df_cols_lower = [str(col).lower() for col in df.columns]
        essenciais_lower = [str(col).lower() for col in colunas_essenciais]
        colunas_faltantes = [col for col in essenciais_lower if col not in df_cols_lower]
        if colunas_faltantes:
            msg_erro = f"Colunas essenciais não encontradas em '{nome_arquivo}': {', '.join(colunas_faltantes)}"
            self.logger.error(msg_erro)
            # self.logger.error(f"      Colunas disponíveis ({len(df.columns)}): {', '.join(map(str, df.columns))}") # Log verboso
            st.error(msg_erro) # Mostra erro na interface Streamlit
            return False
        return True

    def _renomear_colunas_para_padrao(self, df, colunas_essenciais):
        # (Mesma implementação do script original)
        mapa_renomear = {}
        df_cols_lower_map = {str(col).lower(): str(col) for col in df.columns}
        for col_padrao in colunas_essenciais:
            col_padrao_lower = str(col_padrao).lower();
            if col_padrao_lower in df_cols_lower_map:
                col_original = df_cols_lower_map[col_padrao_lower];
                if col_original != col_padrao: mapa_renomear[col_original] = col_padrao
        if mapa_renomear: self.logger.info(f"Renomeando colunas: {mapa_renomear}"); df.rename(columns=mapa_renomear, inplace=True)
        return df

    # MODIFICADO para aceitar uploaded_file em vez de caminho_arquivo
    def carregar_arquivo(self, uploaded_file, colunas_essenciais, tipo_arquivo="Dados"):
        if uploaded_file is None:
            self.logger.error(f"Arquivo {tipo_arquivo} não fornecido.")
            return None

        nome_arquivo = uploaded_file.name
        df = None
        encodings = ['latin-1', 'windows-1252', 'utf-8', 'utf-8-sig']
        try:
            if nome_arquivo.lower().endswith(('.xlsx', '.xls')):
                df = pd.read_excel(uploaded_file, engine=None, dtype=str)
                self.logger.info(f"'{nome_arquivo}' ({tipo_arquivo}) Excel carregado.")
            elif nome_arquivo.lower().endswith('.csv'):
                self.logger.info(f"Carregando CSV {tipo_arquivo}: {nome_arquivo}...")
                # Tenta detectar encoding e separador lendo o início
                # Usar um buffer é mais seguro com UploadedFile
                buffer_preview = io.BytesIO(uploaded_file.getvalue())
                preview_lines = buffer_preview.read(2048).decode('utf-8', errors='ignore') # Lê primeiros 2k bytes

                # Tentar de novo com latin-1 se utf-8 falhou feio
                if '' in preview_lines or not preview_lines:
                     buffer_preview.seek(0)
                     preview_lines = buffer_preview.read(2048).decode('latin-1', errors='ignore')

                sep = ';' if preview_lines.count(';') >= preview_lines.count(',') else ','
                self.logger.debug(f"CSV detectado: sep='{repr(sep)}'")

                # Resetar ponteiro do arquivo original antes de ler com Pandas
                uploaded_file.seek(0)
                read_success = False
                for enc in encodings:
                    try:
                        uploaded_file.seek(0) # Garantir que está no início
                        df = pd.read_csv(uploaded_file, encoding=enc, sep=sep, on_bad_lines='warn', low_memory=False, dtype=str)
                        self.logger.info(f"'{nome_arquivo}' ({tipo_arquivo}) CSV carregado (enc={enc}, sep='{repr(sep)}').")
                        read_success = True
                        break
                    except Exception as e_read:
                        self.logger.debug(f"  Falha ao ler CSV {nome_arquivo} com enc='{enc}': {e_read}")
                        continue
                if not read_success:
                    self.logger.error(f"ERRO: Falha ao carregar CSV '{nome_arquivo}' com todas as tentativas.")
                    st.error(f"Não foi possível ler o arquivo CSV '{nome_arquivo}'. Verifique o formato e encoding.")
                    return None
            else:
                self.logger.error(f"ERRO: Formato não suportado p/ {tipo_arquivo}: '{nome_arquivo}'.")
                st.error(f"Formato de arquivo não suportado para {tipo_arquivo}: {nome_arquivo}")
                return None

            if not self._validar_colunas(df, colunas_essenciais, nome_arquivo): return None
            df = self._renomear_colunas_para_padrao(df, colunas_essenciais)
            self.logger.info(f"'{nome_arquivo}' ({tipo_arquivo}): {df.shape[0]} linhas.")
            self.logger.info(f"Convertendo tipos para {tipo_arquivo}...")

            # Conversões de Tipo (usando nomes de colunas da config)
            cfg = self.config
            cols_to_numeric = []
            cols_to_datetime = []
            cols_to_string_special = []

            if tipo_arquivo == "Cabeçalhos":
                cols_to_numeric = [cfg.COLUNA_ID_PROCESSO]
                cols_to_datetime = [cfg.COLUNA_DATA_AUTUACAO]
                cols_to_string_special = [cfg.COLUNA_NR_PROCESSO, cfg.COLUNA_CLASSE_COD, cfg.COLUNA_ASSUNTO_COD, cfg.COLUNA_CLASSE_NOME]
            elif tipo_arquivo == "Movimentos":
                cols_to_numeric = [cfg.COLUNA_ID_PROCESSO]
                cols_to_datetime = [cfg.COLUNA_MOVIMENTO_DATA]
                cols_to_string_special = [cfg.COLUNA_MOVIMENTO_COD]
            elif tipo_arquivo == "Tarefas":
                cols_to_numeric = [cfg.COLUNA_TAREFA_ID_PROCESSO]
                cols_to_datetime = [cfg.COLUNA_TAREFA_INICIO, cfg.COLUNA_TAREFA_FIM]
                cols_to_string_special = [cfg.COLUNA_TAREFA_FLUXO, cfg.COLUNA_TAREFA_NOME]

            for col in df.columns:
                col_std = str(col) # Garantir que é string
                 # Tratar stripping antes de converter
                if df[col_std].dtype == 'object':
                    df[col_std] = df[col_std].astype(str).str.strip()

                if col_std in cols_to_numeric:
                    df[col_std] = pd.to_numeric(df[col_std], errors='coerce').astype('Int64')
                elif col_std in cols_to_datetime:
                    # Tentar converter explicitamente com dayfirst=True
                    df[col_std] = pd.to_datetime(df[col_std], dayfirst=True, errors='coerce')
                elif col_std in cols_to_string_special:
                    df[col_std] = df[col_std].fillna('').astype(str)

            # Limpar IDs nulos após conversão
            if cfg.COLUNA_ID_PROCESSO in df.columns:
                 df.dropna(subset=[cfg.COLUNA_ID_PROCESSO], inplace=True)

            self.logger.info(f"Conversões {tipo_arquivo} concluídas.")
            return df
        except Exception as e:
            self.logger.error(f"ERRO GERAL carregando {tipo_arquivo} '{nome_arquivo}': {e}")
            self.logger.error(traceback.format_exc())
            st.error(f"Erro geral ao processar o arquivo {tipo_arquivo} '{nome_arquivo}'. Verifique o console/log para detalhes.")
            return None


# =======================================
# Classe IdentificadorProcessosMeta (do script original)
# =======================================
class IdentificadorProcessosMeta:
    # (Implementação mantida exatamente como no script v2.5 corrigido)
    """Identifica IDs de processos relevantes."""
    def __init__(self, config=ConfiguracaoMetas, logger=None):
        self.config = config
        self.logger = logger if logger else logging.getLogger()

    def identificar(self, df_cabecalhos):
        if df_cabecalhos is None or df_cabecalhos.empty: self.logger.error("ERRO: DF Cabeçalhos vazio."); return None
        self.logger.info("Identificando processos relevantes...")
        req_cols = [self.config.COLUNA_ID_PROCESSO, self.config.COLUNA_CLASSE_COD, self.config.COLUNA_CLASSE_NOME, self.config.COLUNA_ASSUNTO_COD]
        if not all(c in df_cabecalhos.columns for c in req_cols):
            msg_erro = f"ERRO: Faltam colunas p/ ID nos Cabeçalhos: {', '.join([c for c in req_cols if c not in df_cabecalhos.columns])}"
            self.logger.error(msg_erro)
            st.error(msg_erro)
            return None
        try:
            for col in [self.config.COLUNA_CLASSE_COD, self.config.COLUNA_ASSUNTO_COD, self.config.COLUNA_CLASSE_NOME]:
                 # Garantir que a coluna existe antes de tentar preencher NA
                 if col in df_cabecalhos.columns:
                      df_cabecalhos[col] = df_cabecalhos[col].fillna('').astype(str)
                 else:
                      # Se a coluna não essencial não existir, criar vazia para evitar erro? Ou logar?
                      self.logger.warning(f"Coluna opcional {col} não encontrada para preenchimento.")

        except Exception as e: self.logger.error(f"ERRO conversão códigos/nomes: {e}"); return None

        mascara_relevante = pd.Series([False]*len(df_cabecalhos), index=df_cabecalhos.index)
        self.logger.info("Aplicando regras de inclusão (Classe/Assunto)...")
        for classe_cod, assuntos in self.config.CLASSES_ASSUNTOS_RELEVANTES.items():
            mascara_classe = (df_cabecalhos[self.config.COLUNA_CLASSE_COD] == classe_cod)
            if not mascara_classe.any(): continue
            if assuntos == ['__TODOS__']: # Compara com lista
                mascara_relevante |= mascara_classe
            elif isinstance(assuntos, list) and assuntos:
                mascara_assunto = df_cabecalhos[self.config.COLUNA_ASSUNTO_COD].isin(assuntos)
                mascara_relevante |= (mascara_classe & mascara_assunto)
        self.logger.info(f"Total após inclusão: {mascara_relevante.sum()}")

        mascara_exclusao = pd.Series([False]*len(df_cabecalhos), index=df_cabecalhos.index)
        if self.config.CLASSE_EXCLUIDA_CODIGO: mascara_exclusao = (df_cabecalhos[self.config.COLUNA_CLASSE_COD] == self.config.CLASSE_EXCLUIDA_CODIGO)
        elif self.config.CLASSE_EXCLUIDA_NOME: mascara_exclusao = (df_cabecalhos[self.config.COLUNA_CLASSE_NOME].astype(str).str.lower() == self.config.CLASSE_EXCLUIDA_NOME.lower())

        if mascara_exclusao.any(): self.logger.info(f"Aplicando exclusão ({mascara_exclusao.sum()})..."); mascara_final = mascara_relevante & (~mascara_exclusao)
        else: mascara_final = mascara_relevante
        self.logger.info(f"Total relevantes final: {mascara_final.sum()}")

        ids_rel = df_cabecalhos.loc[mascara_final, self.config.COLUNA_ID_PROCESSO].unique()
        ids_rel_series = pd.Series(ids_rel).dropna().astype('Int64')
        return ids_rel_series

# ==========================
# Classe CalculadoraMeta1 (Adaptada para receber data_snapshot)
# ==========================
class CalculadoraMeta1:
    """Calcula Meta 1 (P1.2 modificado para incluir todos baixados def. no ANO_META até snapshot)."""
    def __init__(self, config=ConfiguracaoMetas, logger=None):
        self.config = config; self.logger = logger if logger else logging.getLogger()

    # MODIFICADO: Aceita date_limit
    def _find_definitive_archives(self, df_mov_proc, date_limit=None):
        mov_arq=self.config.MOV_ARQUIVAMENTO_DEFINITIVO; mov_desarq=self.config.MOV_DESARQUIVAMENTO
        col_data=self.config.COLUNA_MOVIMENTO_DATA; col_cod=self.config.COLUNA_MOVIMENTO_COD
        if df_mov_proc is None or df_mov_proc.empty: return None, pd.NaT # Retorna None e NaT

        df_mov_work = df_mov_proc.copy()
        df_mov_work[col_data] = pd.to_datetime(df_mov_work[col_data], errors='coerce')
        if date_limit and isinstance(date_limit, datetime):
            df_mov_work = df_mov_work.loc[df_mov_work[col_data] <= date_limit]

        if df_mov_work.empty: return None, pd.NaT

        # Garantir que estamos comparando Timestamps
        last_arq_rows = df_mov_work.loc[df_mov_work[col_cod] == mov_arq]
        last_desarq_rows = df_mov_work.loc[df_mov_work[col_cod] == mov_desarq]

        if last_arq_rows.empty: return None, pd.NaT

        max_dt_arq = last_arq_rows[col_data].max()
        if pd.isna(max_dt_arq): return None, pd.NaT # Arquivado mas sem data válida? Improvável mas seguro

        if last_desarq_rows.empty: return mov_arq, max_dt_arq # Arquivado e nunca desarquivado

        max_dt_desarq = last_desarq_rows[col_data].max()

        # Se não há data de desarquivamento válida ou se arquivamento é posterior
        if pd.isna(max_dt_desarq) or max_dt_arq > max_dt_desarq:
            return mov_arq, max_dt_arq # Arquivado e não desarquivado posteriormente
        else:
            return mov_desarq, max_dt_desarq # Foi arquivado, mas último evento foi desarquivamento

    # MODIFICADO: Aceita data_snapshot
    def calcular(self, df_cabecalhos, df_movimentos, ids_relevantes, data_snapshot):
        if df_cabecalhos is None or df_movimentos is None or ids_relevantes is None: self.logger.error("ERRO [Meta1]: Inputs inválidos."); return None
        self.logger.info(f"Calculando Meta 1 até {data_snapshot.strftime('%d/%m/%Y')}...");
        col_id = self.config.COLUNA_ID_PROCESSO
        df_cabecalhos_rel = df_cabecalhos[df_cabecalhos[col_id].isin(ids_relevantes)].copy()
        df_movimentos_rel = df_movimentos[df_movimentos[col_id].isin(ids_relevantes)].copy()

        # Garantir que ids_relevantes é Series
        if not isinstance(ids_relevantes, pd.Series):
             ids_relevantes = pd.Series(ids_relevantes)

        if ids_relevantes.empty: return {'P1.1': 0, 'P1.2': 0, 'P1.3': 0, 'percentual': 100.0, 'ids_P1.1': [], 'ids_P1.2': [], 'ids_P1.3': []}

        data_inicio_meta = self.config.DATA_INICIO_META
        col_data_aut = self.config.COLUNA_DATA_AUTUACAO
        df_cabecalhos_rel[col_data_aut] = pd.to_datetime(df_cabecalhos_rel[col_data_aut], errors='coerce')

        # P1.1: Distribuídos no ANO_META até a data_snapshot
        mask_p1_1 = (df_cabecalhos_rel[col_data_aut] >= data_inicio_meta) & \
                    (df_cabecalhos_rel[col_data_aut] <= data_snapshot)
        ids_p1_1 = df_cabecalhos_rel.loc[mask_p1_1, col_id].unique().tolist(); p1_1 = len(ids_p1_1); self.logger.info(f"P1.1 = {p1_1}")

        # P1.3: Pendentes no início do ano da meta (status em DATA_FIM_ANO_ANTERIOR)
        data_fim_ano_anterior = self.config.DATA_FIM_ANO_ANTERIOR
        ids_pendentes_inicio_ano = set()
        mov_grouped = df_movimentos_rel.groupby(col_id)

        for proc_id in ids_relevantes:
            # Verifica se foi autuado ANTES do início do ano da meta
            dt_aut_proc = df_cabecalhos_rel.loc[df_cabecalhos_rel[col_id] == proc_id, col_data_aut].iloc[0]
            if pd.notna(dt_aut_proc) and dt_aut_proc < data_inicio_meta:
                df_proc_mov = mov_grouped.get_group(proc_id) if proc_id in mov_grouped.groups else pd.DataFrame()
                # Usar a função _get_terminal_status da Meta 2 para consistência
                # (Precisa instanciar ou mover a função para um local comum)
                # Vamos simplificar aqui e usar _find_definitive_archives
                last_mov_code, last_mov_date = self._find_definitive_archives(df_proc_mov.copy(), data_fim_ano_anterior)
                if last_mov_code != self.config.MOV_ARQUIVAMENTO_DEFINITIVO: # Se não estava arquivado definitivamente no fim do ano anterior
                     ids_pendentes_inicio_ano.add(proc_id)
            elif pd.isna(dt_aut_proc):
                 # Se não tem data de autuação, não pode ter entrado antes. Considerar pendente se relevante?
                 # Por segurança, vamos ignorar processos sem data de autuação válida para P1.3
                 pass

        ids_p1_3 = list(ids_pendentes_inicio_ano)
        p1_3 = len(ids_p1_3); self.logger.info(f"P1.3 = {p1_3}")

        # P1.2: Baixados Definitivamente no ANO_META até a data_snapshot
        ids_p1_2 = []
        for proc_id in ids_relevantes:
            df_proc_mov = mov_grouped.get_group(proc_id) if proc_id in mov_grouped.groups else pd.DataFrame()
            # Verifica status final ATÉ A DATA SNAPSHOT
            last_mov_code, last_mov_date = self._find_definitive_archives(df_proc_mov.copy(), data_snapshot)

            # Verifica se o arquivamento ocorreu DENTRO do ano da meta e ATÉ a data snapshot
            if last_mov_code == self.config.MOV_ARQUIVAMENTO_DEFINITIVO and \
               pd.notna(last_mov_date) and \
               data_inicio_meta <= last_mov_date <= data_snapshot:
                 ids_p1_2.append(proc_id)

        p1_2 = len(ids_p1_2); self.logger.info(f"P1.2 = {p1_2} (Baixados Def. em {self.config.ANO_META} até {data_snapshot.strftime('%d/%m/%Y')})")

        # Percentual (Meta original: P1.2 >= P1.1)
        # Calculando como % de P1.2 em relação a P1.1
        percentual = (p1_2 / p1_1 * 100) if p1_1 > 0 else (100.0 if p1_2 > 0 else 0.0)
        self.logger.info(f"Percentual Meta 1 (P1.2/P1.1) = {percentual:.2f}%")

        return {'P1.1': p1_1, 'P1.2': p1_2, 'P1.3': p1_3, 'percentual': round(percentual, 2), 'ids_P1.1': ids_p1_1, 'ids_P1.2': ids_p1_2, 'ids_P1.3': ids_p1_3}


# ==========================
# Classe CalculadoraMeta2 (Adaptada para data_snapshot)
# ==========================
class CalculadoraMeta2:
    """Calcula Meta 2 (Lógica Corrigida)."""
    def __init__(self, config=ConfiguracaoMetas, logger=None):
        self.config = config; self.logger = logger if logger else logging.getLogger()

    # MODIFICADO: Renomeado date_limit para clareza, retorna status mais detalhado
    def _get_status_processo_em(self, df_mov_proc, date_limit):
        """Retorna PENDING, ARCHIVED_DEFINITIVE, DECIDED_OTHER em date_limit"""
        if df_mov_proc is None or df_mov_proc.empty: return 'PENDING'
        mov_arq=self.config.MOV_ARQUIVAMENTO_DEFINITIVO; mov_desarq=self.config.MOV_DESARQUIVAMENTO
        mov_terminais=self.config.MOVIMENTOS_TERMINAIS; mov_decisao = self.config.MOVIMENTOS_DECISAO
        col_data=self.config.COLUNA_MOVIMENTO_DATA; col_cod=self.config.COLUNA_MOVIMENTO_COD

        df_mov_work = df_mov_proc.copy();
        # Assegurar que a coluna de data é datetime
        df_mov_work[col_data] = pd.to_datetime(df_mov_work[col_data], errors='coerce')
        # Filtrar NAs na data após conversão
        df_mov_work = df_mov_work.dropna(subset=[col_data])

        df_mov_limitado = df_mov_work.loc[df_mov_work[col_data] <= date_limit].copy()

        if df_mov_limitado.empty: return 'PENDING' # Sem movimentos até a data limite

        # Encontra o ÚLTIMO movimento terminal ATÉ a data limite
        df_terminais_limitado = df_mov_limitado[df_mov_limitado[col_cod].isin(mov_terminais)].copy()
        if df_terminais_limitado.empty: return 'PENDING' # Nenhum mov terminal até a data

        try:
            # Ordena pelos mais recentes primeiro
            df_terminais_limitado = df_terminais_limitado.sort_values(col_data, ascending=False)
            ultimo_terminal_event = df_terminais_limitado.iloc[0]
            #idx_ultimo_terminal = df_terminais_limitado[col_data].idxmax() # idxmax pode falhar com NaT
            #if pd.isna(idx_ultimo_terminal): return 'PENDING'
            #ultimo_terminal_event = df_terminais_limitado.loc[idx_ultimo_terminal]

        except (ValueError, IndexError): return 'PENDING' # Se não conseguir achar o último

        ultimo_terminal_code = ultimo_terminal_event[col_cod]; ultimo_terminal_date = ultimo_terminal_event[col_data]
        if pd.isna(ultimo_terminal_date): return 'PENDING' # Data inválida no último terminal?

        # Verifica se houve desarquivamento APÓS este último terminal, mas AINDA DENTRO do limite da data
        desarquivamentos_posteriores = df_mov_limitado[
            (df_mov_limitado[col_cod] == mov_desarq) &
            (df_mov_limitado[col_data] > ultimo_terminal_date)
        ]

        if not desarquivamentos_posteriores.empty:
            return 'PENDING' # Foi reaberto após o último terminal (antes ou na data limite)

        # Se não foi reaberto, o status é definido pelo último terminal
        if ultimo_terminal_code == mov_arq:
            return 'ARCHIVED_DEFINITIVE'
        elif ultimo_terminal_code in mov_decisao:
             return 'DECIDED_OTHER' # Inclui outras decisões terminais
        else:
             # Caso não previsto explicitamente, tratar como pendente por segurança?
             # Ou erro? Vamos assumir que mov_terminais cobre tudo.
             self.logger.warning(f"Movimento terminal {ultimo_terminal_code} não classificado em _get_status_processo_em.")
             return 'PENDING'


    # MODIFICADO: Aceita data_snapshot
    def calcular(self, df_cabecalhos, df_movimentos, ids_relevantes, data_snapshot):
        if df_cabecalhos is None or df_movimentos is None or ids_relevantes is None: self.logger.error("ERRO [Meta2]: Inputs inválidos."); return None
        self.logger.info(f"Calculando Meta 2 até {data_snapshot.strftime('%d/%m/%Y')}...");
        col_id = self.config.COLUNA_ID_PROCESSO
        df_cabecalhos_rel = df_cabecalhos[df_cabecalhos[col_id].isin(ids_relevantes)].copy()
        df_movimentos_rel = df_movimentos[df_movimentos[col_id].isin(ids_relevantes)].copy()

        if not isinstance(ids_relevantes, pd.Series): ids_relevantes = pd.Series(ids_relevantes)
        if ids_relevantes.empty: return {'P2.1': 0, 'P2.2': 0, 'percentual': 100.0, 'ids_P2.1': [], 'ids_P2.2': []}

        # P2.1: Base = Processos relevantes autuados até DATA_CORTE_META2 e PENDENTES no fim do ano anterior
        data_corte_meta2 = self.config.DATA_CORTE_META2
        data_fim_ano_anterior = self.config.DATA_FIM_ANO_ANTERIOR
        col_data_aut = self.config.COLUNA_DATA_AUTUACAO
        df_cabecalhos_rel[col_data_aut] = pd.to_datetime(df_cabecalhos_rel[col_data_aut], errors='coerce')

        mask_p2_1_cand = df_cabecalhos_rel[col_data_aut] <= data_corte_meta2
        ids_candidatos_p2_1 = df_cabecalhos_rel.loc[mask_p2_1_cand, col_id].unique()
        self.logger.info(f"Candidatos P2.1 (autuados até {data_corte_meta2.strftime('%d/%m/%Y')}): {len(ids_candidatos_p2_1)}")
        if len(ids_candidatos_p2_1) == 0: return {'P2.1': 0, 'P2.2': 0, 'percentual': 100.0, 'ids_P2.1': [], 'ids_P2.2': []}

        ids_p2_1_list = []
        mov_cand_grouped = df_movimentos_rel[df_movimentos_rel[col_id].isin(ids_candidatos_p2_1)].groupby(col_id)
        for proc_id in ids_candidatos_p2_1:
            df_proc_mov = mov_cand_grouped.get_group(proc_id) if proc_id in mov_cand_grouped.groups else pd.DataFrame()
            # Verifica o status no FIM DO ANO ANTERIOR
            status_fim_ano = self._get_status_processo_em(df_proc_mov.copy(), data_fim_ano_anterior)
            if status_fim_ano == 'PENDING':
                 ids_p2_1_list.append(proc_id)

        p2_1 = len(ids_p2_1_list)
        self.logger.info(f"P2.1 (Pendentes em {data_fim_ano_anterior.strftime('%d/%m/%Y')} da base de corte) = {p2_1}")
        if p2_1 == 0: return {'P2.1': 0, 'P2.2': 0, 'percentual': 100.0, 'ids_P2.1': [], 'ids_P2.2': []}

        # P2.2: Resolvidos ATÉ data_snapshot DENTRE os da base P2.1
        ids_p2_2_list = []
        mov_p2_1_grouped = df_movimentos_rel[df_movimentos_rel[col_id].isin(ids_p2_1_list)].groupby(col_id)
        for proc_id in ids_p2_1_list:
            df_proc_mov = mov_p2_1_grouped.get_group(proc_id) if proc_id in mov_p2_1_grouped.groups else pd.DataFrame()
            # Verifica o status final ATÉ A DATA SNAPSHOT
            status_final = self._get_status_processo_em(df_proc_mov.copy(), data_snapshot)
            if status_final != 'PENDING': # Se não está pendente, foi resolvido (ARQUIVADO ou DECIDIDO)
                ids_p2_2_list.append(proc_id)

        p2_2 = len(ids_p2_2_list)
        self.logger.info(f"P2.2 (Resolvidos da base P2.1 até {data_snapshot.strftime('%d/%m/%Y')}) = {p2_2}")

        # Percentual
        percentual = (p2_2 / p2_1 * 100) if p2_1 > 0 else 100.0
        self.logger.info(f"Percentual Meta 2 = {percentual:.2f}%")
        return {'P2.1': p2_1, 'P2.2': p2_2, 'percentual': round(percentual, 2), 'ids_P2.1': ids_p2_1_list, 'ids_P2.2': ids_p2_2_list}


# ==========================
# Classe CalculadoraMeta3 (Adaptada para data_snapshot)
# ==========================
class CalculadoraMeta3:
    """Calcula Meta 3 (Adaptada: Decidir em até PRAZO_DIAS_META3 dias)."""
    def __init__(self, config=ConfiguracaoMetas, logger=None):
        self.config = config; self.logger = logger if logger else logging.getLogger()

    # MODIFICADO: Aceita date_limit
    def _find_first_decision_date_in_year(self, df_mov_proc, decision_codes_set, start_date, end_date):
        """Encontra a data da primeira decisão DENTRO do intervalo [start_date, end_date]."""
        if df_mov_proc is None or df_mov_proc.empty: return pd.NaT
        col_data=self.config.COLUNA_MOVIMENTO_DATA; col_cod=self.config.COLUNA_MOVIMENTO_COD

        df_mov_work = df_mov_proc.copy()
        df_mov_work[col_data] = pd.to_datetime(df_mov_work[col_data], errors='coerce')

        # Filtra por códigos de decisão E pelo intervalo de datas
        decision_mask = df_mov_work[col_cod].isin(decision_codes_set)
        date_mask = (df_mov_work[col_data] >= start_date) & (df_mov_work[col_data] <= end_date)
        df_decisions_in_period = df_mov_work.loc[decision_mask & date_mask]

        if df_decisions_in_period.empty: return pd.NaT

        # Encontra a data mínima (primeira decisão)
        min_date = df_decisions_in_period[col_data].min()
        return pd.NaT if pd.isna(min_date) else min_date

    # MODIFICADO: Aceita data_snapshot
    def calcular(self, df_cabecalhos, df_movimentos, ids_relevantes, data_snapshot):
        if df_cabecalhos is None or df_movimentos is None or ids_relevantes is None: self.logger.error("ERRO [Meta3]: Inputs inválidos."); return None
        self.logger.info(f"Calculando Meta 3 (Adaptada) até {data_snapshot.strftime('%d/%m/%Y')}...");
        col_id=self.config.COLUNA_ID_PROCESSO; col_data_aut=self.config.COLUNA_DATA_AUTUACAO
        df_cabecalhos_rel = df_cabecalhos[df_cabecalhos[col_id].isin(ids_relevantes)].copy()
        df_movimentos_rel = df_movimentos[df_movimentos[col_id].isin(ids_relevantes)].copy()

        if not isinstance(ids_relevantes, pd.Series): ids_relevantes = pd.Series(ids_relevantes)
        if ids_relevantes.empty: return {'P3.1': 0, 'P3.2': 0, 'percentual': 100.0, 'details_P3.1': {}, 'details_P3.2': {}}

        df_cabecalhos_rel[col_data_aut] = pd.to_datetime(df_cabecalhos_rel[col_data_aut], errors='coerce')
        # Mapeia apenas processos relevantes com data de autuação válida
        map_id_data_autuacao = df_cabecalhos_rel.dropna(subset=[col_data_aut]).set_index(col_id)[col_data_aut].to_dict()
        self.logger.debug(f"Map ID->Autuação (Meta3) criado para {len(map_id_data_autuacao)} processos relevantes.")

        # P3.1: Processos com primeira decisão no ANO_META até data_snapshot
        processos_p3_1_details = {} # {proc_id: data_primeira_decisao}
        decision_codes = self.config.MOVIMENTOS_DECISAO # Usar apenas decisões, não baixas
        data_inicio_meta = self.config.DATA_INICIO_META
        # Limitar end_date pela data_snapshot E pelo fim do ano da meta
        end_date_limit = min(data_snapshot, self.config.DATA_FIM_META)

        mov_rel_grouped = df_movimentos_rel.groupby(col_id)
        # Iterar apenas sobre IDs relevantes que TEM data de autuação
        for proc_id in map_id_data_autuacao.keys():
            if proc_id not in ids_relevantes.values: continue # Segurança extra

            df_proc_mov = mov_rel_grouped.get_group(proc_id) if proc_id in mov_rel_grouped.groups else pd.DataFrame()
            dt_primeira_decisao = self._find_first_decision_date_in_year(
                df_proc_mov.copy(), decision_codes, data_inicio_meta, end_date_limit
            )
            if not pd.isna(dt_primeira_decisao):
                processos_p3_1_details[proc_id] = dt_primeira_decisao

        p3_1 = len(processos_p3_1_details)
        self.logger.info(f"P3.1 = {p3_1} (Decididos em {self.config.ANO_META} até {data_snapshot.strftime('%d/%m/%Y')})")
        if p3_1 == 0: return {'P3.1': 0, 'P3.2': 0, 'percentual': 100.0, 'details_P3.1': {}, 'details_P3.2': {}}

        # P3.2: Decididos (P3.1) dentro do prazo de PRAZO_DIAS_META3
        processos_p3_2_details = {} # {proc_id: {'dt_autuacao': ..., 'dt_decisao': ..., 'delta_dias': ...}}
        prazo_maximo_dias = self.config.PRAZO_DIAS_META3
        for proc_id, dt_decisao in processos_p3_1_details.items():
            dt_autuacao = map_id_data_autuacao.get(proc_id) # Já garantido que existe e não é NaT
            delta_dias = (dt_decisao - dt_autuacao).days
            # Considerar apenas positivos e dentro do prazo
            if 0 <= delta_dias <= prazo_maximo_dias:
                 processos_p3_2_details[proc_id] = {'dt_autuacao': dt_autuacao, 'dt_decisao': dt_decisao, 'delta_dias': delta_dias}

        p3_2 = len(processos_p3_2_details)
        self.logger.info(f"P3.2 = {p3_2} (Decididos no prazo de {prazo_maximo_dias} dias)")

        # Percentual
        percentual = (p3_2 / p3_1 * 100) if p3_1 > 0 else 100.0
        self.logger.info(f"Percentual Meta 3 = {percentual:.2f}%")
        return {'P3.1': p3_1, 'P3.2': p3_2, 'percentual': round(percentual, 2),
                'details_P3.1': processos_p3_1_details, 'details_P3.2': processos_p3_2_details}


# ==========================
# Classe AnalisadorMetas (Adaptada para aceitar DataFrames e data_snapshot)
# ==========================
class AnalisadorMetas:
    """Orquestra a análise completa para uma data snapshot."""
    def __init__(self, config=ConfiguracaoMetas, logger=None):
        self.config = config
        self.logger = logger if logger else logging.getLogger()
        # Não armazena mais DFs internamente, recebe como parâmetro

    # MODIFICADO: Recebe DataFrames e data_snapshot
    def executar_analise(self, df_cabecalhos, df_movimentos, df_tarefas, data_snapshot):
        """Executa análise e retorna resultados."""
        self.logger.info(f">>> INICIANDO ANÁLISE SNAPSHOT PARA {data_snapshot.strftime('%d/%m/%Y')} <<<")

        # 1. Validação Básica dos Dados de Entrada
        if df_cabecalhos is None or df_movimentos is None or df_tarefas is None:
             st.error("Um ou mais DataFrames de entrada estão faltando.")
             self.logger.error("ERRO: DataFrames de entrada ausentes em executar_analise.")
             return None # Falha na análise

        # 2. Identificação
        self.logger.info("--- Etapa 1: Identificando Processos Relevantes ---")
        identificador = IdentificadorProcessosMeta(config=self.config, logger=self.logger)
        ids_relevantes = identificador.identificar(df_cabecalhos.copy()) # Usa cópia para não alterar original
        if ids_relevantes is None:
             st.error("Falha ao identificar processos relevantes.")
             return None # Falha na análise
        if ids_relevantes.empty:
             self.logger.warning("Nenhum processo relevante identificado.")
             st.warning("Nenhum processo relevante encontrado para análise.")
             # Retornar resultados vazios em vez de None para permitir gerar relatório vazio
             return {'resultados': {'meta1': {}, 'meta2': {}, 'meta3': {}},
                     'ids_relevantes': ids_relevantes,
                     'dfs_detalhes_metas': {},
                     'resultados_tarefas': {'tarefas_ativas': pd.DataFrame(), 'duracao_historica': pd.DataFrame(), 'df_tarefas_ativas_com_idade': pd.DataFrame()},
                     'df_cabecalhos_rel': pd.DataFrame()}


        self.logger.info(f"--- Encontrados {len(ids_relevantes)} processos relevantes ---")

        # 3. Cálculo das Metas (Passando data_snapshot)
        self.logger.info("--- Etapa 2: Calculando Indicadores das Metas ---")
        resultados_metas = {}
        calculadoras = {'meta1': CalculadoraMeta1, 'meta2': CalculadoraMeta2, 'meta3': CalculadoraMeta3}
        dfs_detalhes_metas_acumulado = {} # Para armazenar listas de IDs/detalhes de Px.y

        for nome, ClasseCalc in calculadoras.items():
            try:
                self.logger.info(f"Calculando {nome.upper()}...")
                calc = ClasseCalc(config=self.config, logger=self.logger)
                # Passar data_snapshot para a função calcular de cada meta
                res = calc.calcular(df_cabecalhos, df_movimentos, ids_relevantes, data_snapshot)
                resultados_metas[nome] = res if res else {}

                # Extrair listas de IDs/detalhes para o relatório
                if res:
                     self.logger.info(f"{nome.upper()} calculada: {res.get('percentual', 'N/A'):.2f}%")
                     for key, value in res.items():
                         if key.startswith('ids_') or key.startswith('details_'):
                             dfs_detalhes_metas_acumulado[f"{nome}_{key}"] = value # Armazena a lista/dict
                else:
                     self.logger.error(f"Falha no cálculo de {nome.upper()}. Resultado vazio.")
                     st.warning(f"Cálculo da {nome.upper()} retornou vazio.")

            except Exception as e:
                self.logger.error(f"ERRO INESPERADO {nome.upper()}: {e}")
                self.logger.error(traceback.format_exc())
                st.error(f"Erro inesperado ao calcular {nome.upper()}. Verifique os logs.")
                resultados_metas[nome] = {} # Garante que a chave existe

        # 4. Análise de Tarefas (para pendentes na data_snapshot)
        self.logger.info("--- Etapa 3: Analisando Tarefas Pendentes ---")
        # Precisamos saber quem está pendente na data snapshot
        ids_pendentes_snapshot = []
        calc_m2_helper = CalculadoraMeta2(config=self.config, logger=self.logger) # Reutilizar helper
        mov_rel_grouped = df_movimentos[df_movimentos[self.config.COLUNA_ID_PROCESSO].isin(ids_relevantes)].groupby(self.config.COLUNA_ID_PROCESSO)

        for proc_id in ids_relevantes:
             df_proc_mov = mov_rel_grouped.get_group(proc_id) if proc_id in mov_rel_grouped.groups else pd.DataFrame()
             status_snapshot = calc_m2_helper._get_status_processo_em(df_proc_mov.copy(), data_snapshot)
             if status_snapshot == 'PENDING':
                 ids_pendentes_snapshot.append(proc_id)

        resultados_tarefas = self._analisar_tarefas_detalhado(df_tarefas, ids_pendentes_snapshot, data_snapshot)

        # 5. Gerar DataFrames de Detalhes (para Excel e Gráficos)
        dfs_detalhes_finais = self._criar_dfs_detalhes_metas(dfs_detalhes_metas_acumulado, df_cabecalhos)
        # Adicionar lista de pendentes ao detalhes finais
        map_id_nr = GeradorRelatorio(config=self.config, logger=self.logger)._criar_map_id_nrprocesso(df_cabecalhos) # Reusar helper
        if ids_pendentes_snapshot:
            df_pend_snap = pd.DataFrame({self.config.COLUNA_ID_PROCESSO: ids_pendentes_snapshot})
            df_pend_snap[self.config.COLUNA_NR_PROCESSO] = df_pend_snap[self.config.COLUNA_ID_PROCESSO].map(map_id_nr).fillna('N/A')
            dfs_detalhes_finais['Pendentes_Snapshot'] = df_pend_snap[[self.config.COLUNA_NR_PROCESSO, self.config.COLUNA_ID_PROCESSO]]
        else:
            dfs_detalhes_finais['Pendentes_Snapshot'] = pd.DataFrame(columns=[self.config.COLUNA_NR_PROCESSO, self.config.COLUNA_ID_PROCESSO])


        self.logger.info(">>> ANÁLISE SNAPSHOT CONCLUÍDA <<<")
        return {
            'resultados_metas': resultados_metas,
            'ids_relevantes': ids_relevantes,
            'dfs_detalhes_metas': dfs_detalhes_finais, # DataFrames prontos
            'resultados_tarefas': resultados_tarefas, # DFs com análise de tarefas
            'df_cabecalhos_rel': df_cabecalhos[df_cabecalhos[self.config.COLUNA_ID_PROCESSO].isin(ids_relevantes)].copy() # Cabeçalhos relevantes para gráficos/excel
        }

    # Função auxiliar movida para dentro ou chamada estaticamente
    def _analisar_tarefas_detalhado(self, df_tarefas, ids_processos_pendentes, data_snapshot):
        """Analisa tarefas para processos pendentes (lógica similar à anterior)."""
        # (Reutiliza a lógica da função analisar_tarefas definida no código anterior)
        resultados_tarefas = {
            'tarefas_ativas': pd.DataFrame(),
            'duracao_historica': pd.DataFrame(),
            'df_tarefas_ativas_com_idade': pd.DataFrame()
        }
        if df_tarefas is None or df_tarefas.empty or not ids_processos_pendentes:
            self.logger.warning("Sem tarefas ou processos pendentes para analisar.")
            return resultados_tarefas

        cfg = self.config
        try:
            df_tarefas_rel = df_tarefas[df_tarefas[cfg.COLUNA_TAREFA_ID_PROCESSO].isin(ids_processos_pendentes)].copy()
            if df_tarefas_rel.empty:
                 self.logger.warning("Nenhuma tarefa encontrada para os processos pendentes selecionados.")
                 return resultados_tarefas

            # 1. Tarefas Ativas
            ativas = df_tarefas_rel[
                (df_tarefas_rel[cfg.COLUNA_TAREFA_INICIO].notna()) & # Precisa ter data de inicio
                (df_tarefas_rel[cfg.COLUNA_TAREFA_INICIO] <= data_snapshot) &
                (df_tarefas_rel[cfg.COLUNA_TAREFA_FIM].isnull() | (df_tarefas_rel[cfg.COLUNA_TAREFA_FIM] > data_snapshot))
            ].copy()

            if not ativas.empty:
                ativas.sort_values(by=[cfg.COLUNA_TAREFA_ID_PROCESSO, cfg.COLUNA_TAREFA_INICIO], ascending=[True, False], inplace=True)
                df_tarefas_ativas = ativas.drop_duplicates(subset=[cfg.COLUNA_TAREFA_ID_PROCESSO], keep='first').copy() # Adiciona .copy()
                df_tarefas_ativas['FLUXO_TAREFA'] = df_tarefas_ativas[cfg.COLUNA_TAREFA_FLUXO].fillna('') + " > " + df_tarefas_ativas[cfg.COLUNA_TAREFA_NOME].fillna('')
                resultados_tarefas['tarefas_ativas'] = df_tarefas_ativas
            else:
                 self.logger.info("Nenhuma tarefa ativa encontrada para os processos pendentes.")


            # 2. Duração Histórica
            concluidas = df_tarefas_rel[
                df_tarefas_rel[cfg.COLUNA_TAREFA_FIM].notna() & \
                (df_tarefas_rel[cfg.COLUNA_TAREFA_FIM] <= data_snapshot) & \
                df_tarefas_rel[cfg.COLUNA_TAREFA_INICIO].notna()
            ].copy() # Adiciona .copy()

            if not concluidas.empty:
                # Calcular duração apenas se fim > inicio
                valid_duration_mask = concluidas[cfg.COLUNA_TAREFA_FIM] > concluidas[cfg.COLUNA_TAREFA_INICIO]
                concluidas_valid = concluidas[valid_duration_mask].copy() # Adiciona .copy()
                if not concluidas_valid.empty:
                     concluidas_valid['DURACAO_DIAS'] = (concluidas_valid[cfg.COLUNA_TAREFA_FIM] - concluidas_valid[cfg.COLUNA_TAREFA_INICIO]).dt.total_seconds() / (60*60*24)
                     concluidas_valid['FLUXO_TAREFA'] = concluidas_valid[cfg.COLUNA_TAREFA_FLUXO].fillna('') + " > " + concluidas_valid[cfg.COLUNA_TAREFA_NOME].fillna('')
                     resultados_tarefas['duracao_historica'] = concluidas_valid[['FLUXO_TAREFA', 'DURACAO_DIAS']] # Apenas colunas necessárias

            # 3. Idade na Tarefa Atual
            df_tarefas_ativas = resultados_tarefas['tarefas_ativas'] # Pega o DF calculado acima
            if not df_tarefas_ativas.empty:
                df_idade = df_tarefas_ativas[[cfg.COLUNA_TAREFA_ID_PROCESSO, 'FLUXO_TAREFA', cfg.COLUNA_TAREFA_INICIO]].copy() # Adiciona .copy()
                df_idade['DIAS_NA_TAREFA'] = (data_snapshot - df_idade[cfg.COLUNA_TAREFA_INICIO]).dt.total_seconds() / (60*60*24)
                df_idade['DIAS_NA_TAREFA'] = df_idade['DIAS_NA_TAREFA'].fillna(0).clip(lower=0).astype(int) # Garante não negativo

                bins = [-1, 30, 90, 180, float('inf')]
                labels = ['0-30 dias', '31-90 dias', '91-180 dias', '> 180 dias']
                df_idade['FAIXA_IDADE_TAREFA'] = pd.cut(df_idade['DIAS_NA_TAREFA'], bins=bins, labels=labels, right=True)
                resultados_tarefas['df_tarefas_ativas_com_idade'] = df_idade

            self.logger.info("Análise de tarefas concluída.")
            return resultados_tarefas

        except Exception as e_task:
             self.logger.error(f"Erro na análise detalhada de tarefas: {e_task}")
             self.logger.error(traceback.format_exc())
             st.error(f"Erro ao analisar tarefas: {e_task}")
             # Retornar resultados vazios em caso de erro
             return {'tarefas_ativas': pd.DataFrame(), 'duracao_historica': pd.DataFrame(), 'df_tarefas_ativas_com_idade': pd.DataFrame()}


    def _criar_dfs_detalhes_metas(self, detalhes_acumulados, df_cabecalhos):
        """Cria DataFrames formatados para listas de IDs/detalhes das metas."""
        dfs_detalhes = {}
        map_id_nr = GeradorRelatorio(config=self.config, logger=self.logger)._criar_map_id_nrprocesso(df_cabecalhos) # Reusar helper

        mapa_nomes = { # Mapeia nomes internos para nomes de aba/coluna mais amigáveis
            'meta1_ids_P1.1': 'P1.1_Distr_Meta',
            'meta1_ids_P1.2': 'P1.2_Resolv_Meta',
            'meta1_ids_P1.3': 'P1.3_Pend_Inicio_Meta',
            'meta2_ids_P2.1': 'P2.1_Base_Meta2',
            'meta2_ids_P2.2': 'P2.2_Resolv_Meta2',
            'meta3_details_P3.1': 'P3.1_Decid_Meta', # Chave é ID, valor é data
            'meta3_details_P3.2': 'P3.2_Decid_Prazo' # Chave é ID, valor é dict com detalhes
        }

        for nome_interno, dados in detalhes_acumulados.items():
            nome_final = mapa_nomes.get(nome_interno)
            if not nome_final: continue # Ignora se não mapeado

            lista_ids = []
            detalhes_extra = None # Para P3.2

            if isinstance(dados, list):
                lista_ids = dados
            elif isinstance(dados, dict):
                lista_ids = list(dados.keys())
                if nome_interno == 'meta3_details_P3.2': # Guardar detalhes para P3.2
                     detalhes_extra = dados

            if lista_ids:
                 df = pd.DataFrame({self.config.COLUNA_ID_PROCESSO: lista_ids})
                 df[self.config.COLUNA_NR_PROCESSO] = df[self.config.COLUNA_ID_PROCESSO].map(map_id_nr).fillna('N/A')

                 # Adicionar colunas extras para P3.2
                 if detalhes_extra:
                      df['Dt. Autuação'] = df[self.config.COLUNA_ID_PROCESSO].map(lambda x: detalhes_extra[x]['dt_autuacao'].strftime('%d/%m/%Y') if x in detalhes_extra else '')
                      df['Dt. Decisão'] = df[self.config.COLUNA_ID_PROCESSO].map(lambda x: detalhes_extra[x]['dt_decisao'].strftime('%d/%m/%Y') if x in detalhes_extra else '')
                      df['Dias P/ Decidir'] = df[self.config.COLUNA_ID_PROCESSO].map(lambda x: detalhes_extra[x]['delta_dias'] if x in detalhes_extra else '')
                      dfs_detalhes[nome_final] = df[[self.config.COLUNA_NR_PROCESSO, self.config.COLUNA_ID_PROCESSO, 'Dt. Autuação', 'Dt. Decisão', 'Dias P/ Decidir']]
                 else:
                      dfs_detalhes[nome_final] = df[[self.config.COLUNA_NR_PROCESSO, self.config.COLUNA_ID_PROCESSO]]
            else:
                 # Criar DF vazio com colunas corretas
                 if nome_interno == 'meta3_details_P3.2':
                      cols = [self.config.COLUNA_NR_PROCESSO, self.config.COLUNA_ID_PROCESSO, 'Dt. Autuação', 'Dt. Decisão', 'Dias P/ Decidir']
                 else:
                      cols = [self.config.COLUNA_NR_PROCESSO, self.config.COLUNA_ID_PROCESSO]
                 dfs_detalhes[nome_final] = pd.DataFrame(columns=cols)

        return dfs_detalhes


# ==========================
# Classe GeradorRelatorio (Adaptada para buffer e receber DFs de detalhes)
# ==========================
class GeradorRelatorio:
    """Gera relatório Excel com Sumário, Abas por Indicador e Abas de Ação com Tarefas."""
    def __init__(self, config=ConfiguracaoMetas, logger=None):
        self.config = config
        self.logger = logger if logger else logging.getLogger()
        self._calculadora_m2_helper = CalculadoraMeta2(config=config, logger=logger) # Reuso do helper _get_status_processo_em

    # Helper mantido
    def _criar_map_id_nrprocesso(self, df_cabecalhos):
        # (Mesma implementação do script original)
        col_id = self.config.COLUNA_ID_PROCESSO; col_nr = self.config.COLUNA_NR_PROCESSO
        if df_cabecalhos is None or col_id not in df_cabecalhos.columns or col_nr not in df_cabecalhos.columns: return {}
        try:
            map_id_nr = df_cabecalhos.dropna(subset=[col_id, col_nr]).astype({col_id: 'Int64', col_nr: str}).set_index(col_id)[col_nr].to_dict()
            return {k: v for k, v in map_id_nr.items() if pd.notna(k)}
        except Exception as e: self.logger.error(f"Erro map ID->NrProcesso: {e}"); return {}


    # Helper mantido (embora DFs de detalhes agora sejam criados no Analisador)
    def _criar_df_lista_processos(self, df_detalhe_existente):
        # Apenas garante as colunas, o DF já vem pronto
        if df_detalhe_existente is None or df_detalhe_existente.empty:
             return pd.DataFrame(columns=[self.config.COLUNA_NR_PROCESSO, self.config.COLUNA_ID_PROCESSO])
        return df_detalhe_existente

    # Helper mantido
    def _criar_df_sumario(self, resultados_metas):
        # (Mesma implementação do script original)
         sumario_data = {
             'Meta': ['Meta 1', 'Meta 2 (Corrigida)', 'Meta 3 (Adapt)'],
             'Indicador Base': [f"P1.1 Distr. {self.config.ANO_META}", f"P2.1 Base Antigos", f"P3.1 Decid. {self.config.ANO_META}"],
             'Valor Base': [resultados_metas.get('meta1', {}).get('P1.1', 'N/A'), resultados_metas.get('meta2', {}).get('P2.1', 'N/A'), resultados_metas.get('meta3', {}).get('P3.1', 'N/A')],
             'Indicador Meta': [f"P1.2 Resolv. {self.config.ANO_META}", f"P2.2 Resolv. Base", f"P3.2 Decid. Prazo"],
             'Valor Meta': [resultados_metas.get('meta1', {}).get('P1.2', 'N/A'), resultados_metas.get('meta2', {}).get('P2.2', 'N/A'), resultados_metas.get('meta3', {}).get('P3.2', 'N/A')],
             'Percentual (%)': [f"{resultados_metas.get('meta1', {}).get('percentual', 0.0):.2f}", f"{resultados_metas.get('meta2', {}).get('percentual', 0.0):.2f}", f"{resultados_metas.get('meta3', {}).get('percentual', 0.0):.2f}"],
             'Info Extra': [f"P1.3 Acervo Início = {resultados_metas.get('meta1', {}).get('P1.3', 'N/A')}", f"Corte P2.1: {self.config.DATA_CORTE_META2.strftime('%d/%m/%Y')}", f"Prazo P3.2 <= {self.config.PRAZO_DIAS_META3} dias"]
         }
         return pd.DataFrame(sumario_data)

    # Helper mantido
    def _criar_map_tarefa_atual(self, df_tarefas_ativas):
         # Recebe o DF já filtrado e ordenado
         self.logger.info("Criando map ID -> Tarefa Atual...")
         if df_tarefas_ativas is None or df_tarefas_ativas.empty: return {}
         col_id = self.config.COLUNA_TAREFA_ID_PROCESSO
         if 'FLUXO_TAREFA' not in df_tarefas_ativas.columns or col_id not in df_tarefas_ativas.columns:
             self.logger.error("ERRO: Colunas necessárias não encontradas em df_tarefas_ativas.")
             return {}

         # O DF já contém as últimas tarefas ativas por ID
         try:
             map_tarefas = pd.Series(df_tarefas_ativas['FLUXO_TAREFA'].values, index=df_tarefas_ativas[col_id]).to_dict()
             self.logger.info(f"Map ID->Tarefa Atual criado para {len(map_tarefas)} processos.")
             return map_tarefas
         except Exception as e:
              self.logger.error(f"Erro ao criar map ID->Tarefa Atual: {e}")
              return {}


    # Helper adaptado para usar DFs pré-calculados
    def _criar_df_pendentes_com_tarefa(self, df_base, df_resolvidos, map_id_tarefa, df_cabecalhos_ref):
        """Cria DataFrame de pendentes com Nr Processo, ID, Tarefa Atual e outras infos."""
        if df_base is None or df_resolvidos is None or df_cabecalhos_ref is None: return pd.DataFrame()
        col_id = self.config.COLUNA_ID_PROCESSO
        if col_id not in df_base.columns or col_id not in df_resolvidos.columns: return pd.DataFrame()

        try:
            ids_base = set(df_base[col_id].astype('Int64').dropna())
            ids_resolvidos = set(df_resolvidos[col_id].astype('Int64').dropna())
            ids_pendentes = list(ids_base - ids_resolvidos)

            if not ids_pendentes: return pd.DataFrame()

            df = pd.DataFrame({col_id: ids_pendentes})
            # Usar merge com df_cabecalhos_ref para pegar NrProcesso, Classe, Data Autuação
            df_merged = pd.merge(
                df,
                df_cabecalhos_ref[[col_id, self.config.COLUNA_NR_PROCESSO, self.config.COLUNA_CLASSE_NOME, self.config.COLUNA_DATA_AUTUACAO]],
                on=col_id,
                how='left'
            )
            df_merged['Tarefa Atual'] = df_merged[col_id].map(map_id_tarefa).fillna('Sem tarefa ativa')
            df_merged[self.config.COLUNA_DATA_AUTUACAO] = pd.to_datetime(df_merged[self.config.COLUNA_DATA_AUTUACAO], errors='coerce').dt.strftime('%d/%m/%Y').fillna('N/A')
            df_merged.rename(columns={self.config.COLUNA_CLASSE_NOME: 'Classe Judicial', self.config.COLUNA_DATA_AUTUACAO: 'Data Autuação'}, inplace=True)

            return df_merged[[self.config.COLUNA_NR_PROCESSO, col_id, 'Tarefa Atual', 'Classe Judicial', 'Data Autuação']].fillna('N/A')

        except Exception as e:
            self.logger.warning(f"Erro ao criar DF pendentes com tarefa: {e}")
            return pd.DataFrame()


    # Helper adaptado para usar DFs pré-calculados
    def _criar_df_pendentes_prazo_meta3_com_tarefa(self, df_pendentes_snapshot, map_id_tarefa, df_cabecalhos_ref, data_snapshot):
         """Cria DataFrame de processos pendentes com prazo e tarefa para Meta 3."""
         if df_pendentes_snapshot is None or df_pendentes_snapshot.empty or df_cabecalhos_ref is None: return pd.DataFrame()
         self.logger.info("Formatando processos pendentes com prazo/tarefa Meta 3...")
         col_id=self.config.COLUNA_ID_PROCESSO; col_data_aut=self.config.COLUNA_DATA_AUTUACAO
         prazo = self.config.PRAZO_DIAS_META3

         try:
             df_pend_com_info = pd.merge(
                 df_pendentes_snapshot[[col_id, self.config.COLUNA_NR_PROCESSO]], # Já tem ID e NrProc
                 df_cabecalhos_ref[[col_id, self.config.COLUNA_CLASSE_NOME, col_data_aut]],
                 on=col_id,
                 how='left'
             )
             df_pend_com_info['Tarefa Atual'] = df_pend_com_info[col_id].map(map_id_tarefa).fillna('Sem tarefa ativa')
             df_pend_com_info[col_data_aut] = pd.to_datetime(df_pend_com_info[col_data_aut], errors='coerce')
             df_pend_com_info.dropna(subset=[col_data_aut], inplace=True) # Precisa da data de autuação

             if df_pend_com_info.empty: return pd.DataFrame()

             df_pend_com_info['Data Limite'] = df_pend_com_info[col_data_aut] + timedelta(days=prazo)
             df_pend_com_info['Dias Restantes'] = (df_pend_com_info['Data Limite'] - data_snapshot).dt.days
             df_pend_com_info['Data Limite Format'] = df_pend_com_info['Data Limite'].dt.strftime('%d/%m/%Y')
             df_pend_com_info['Data Autuação Format'] = df_pend_com_info[col_data_aut].dt.strftime('%d/%m/%Y')

             df_final = df_pend_com_info[[
                 self.config.COLUNA_NR_PROCESSO, col_id, 'Tarefa Atual',
                 self.config.COLUNA_CLASSE_NOME, 'Data Autuação Format',
                 'Data Limite Format', 'Dias Restantes'
             ]].copy() # Adiciona .copy()
             df_final.rename(columns={
                 self.config.COLUNA_CLASSE_NOME: 'Classe Judicial',
                 'Data Autuação Format': 'Data Autuação',
                 'Data Limite Format': f'Data Limite ({prazo}d)'
             }, inplace=True)

             return df_final.sort_values(by='Dias Restantes', ascending=True)

         except Exception as e:
              self.logger.error(f"Erro ao criar DF Pendentes Prazo Meta 3: {e}")
              return pd.DataFrame()


    # MODIFICADO: Aceita buffer e recebe dados_analise completos
    def salvar_relatorio(self, dados_analise, buffer_saida):
        """Salva relatório Excel em um buffer com Sumário, Abas por Indicador e Abas de Ação com Tarefas."""
        try:
            import xlsxwriter # Verificar se está instalado
        except ImportError:
             self.logger.error("ERRO: 'xlsxwriter' não instalado. Não é possível gerar Excel.")
             st.error("Biblioteca 'xlsxwriter' necessária. Instale com 'pip install xlsxwriter'")
             return False

        if not dados_analise: self.logger.error("Dados de análise inválidos p/ relatório."); return False
        resultados_metas = dados_analise.get('resultados_metas')
        dfs_detalhes_metas = dados_analise.get('dfs_detalhes_metas')
        resultados_tarefas = dados_analise.get('resultados_tarefas')
        df_cabecalhos_rel = dados_analise.get('df_cabecalhos_rel')
        ids_relevantes = dados_analise.get('ids_relevantes') # Pode ser Series

        # Validação mínima dos dados necessários
        if not resultados_metas or not dfs_detalhes_metas or not resultados_tarefas or df_cabecalhos_rel is None:
             self.logger.error("Dados insuficientes nos resultados da análise para gerar relatório completo.")
             st.error("Dados insuficientes para gerar o relatório Excel completo.")
             return False

        map_id_tarefa = self._criar_map_tarefa_atual(resultados_tarefas.get('tarefas_ativas'))
        if not map_id_tarefa: self.logger.warning("Mapeamento ID->Tarefa Atual vazio.")

        self.logger.info("Gerando relatório final em buffer...")
        try:
            with pd.ExcelWriter(buffer_saida, engine='xlsxwriter', datetime_format='dd/mm/yyyy', date_format='dd/mm/yyyy') as writer:
                # Aba Sumário
                df_sumario = self._criar_df_sumario(resultados_metas)
                df_sumario.to_excel(writer, sheet_name='Sumario', index=False)
                self.logger.debug("Aba Sumário escrita.")

                # Abas de Ação (Pendentes com Tarefa)
                df_pend_m1 = self._criar_df_pendentes_com_tarefa(
                     dfs_detalhes_metas.get('P1.1_Distr_Meta'),
                     dfs_detalhes_metas.get('P1.2_Resolv_Meta'),
                     map_id_tarefa, df_cabecalhos_rel
                )
                if not df_pend_m1.empty: df_pend_m1.to_excel(writer, sheet_name='Acao_Meta1_Pendentes', index=False)
                self.logger.debug("Aba Acao_Meta1 escrita.")


                df_pend_m2 = self._criar_df_pendentes_com_tarefa(
                     dfs_detalhes_metas.get('P2.1_Base_Meta2'),
                     dfs_detalhes_metas.get('P2.2_Resolv_Meta2'),
                     map_id_tarefa, df_cabecalhos_rel
                )
                if not df_pend_m2.empty: df_pend_m2.to_excel(writer, sheet_name='Acao_Meta2_Pendentes', index=False)
                self.logger.debug("Aba Acao_Meta2 escrita.")

                df_prazos_m3 = self._criar_df_pendentes_prazo_meta3_com_tarefa(
                    dfs_detalhes_metas.get('Pendentes_Snapshot'), # DF de pendentes já calculado
                    map_id_tarefa,
                    df_cabecalhos_rel,
                    datetime.now() # Ou passar a data_snapshot real? Passando now por enquanto. ** Melhorar: Passar data_snapshot **
                    # TODO: Passar a data_snapshot para a função _criar_df_pendentes_prazo_meta3_com_tarefa
                )
                if not df_prazos_m3.empty: df_prazos_m3.to_excel(writer, sheet_name='Acao_Meta3_Pend_Prazo', index=False)
                self.logger.debug("Aba Acao_Meta3 escrita.")
                self.logger.info("Abas de Ação criadas.")


                # Abas por Indicador Px.y (Detalhe)
                # Usar os DataFrames já criados em dfs_detalhes_metas
                for nome_aba, df_detalhe in dfs_detalhes_metas.items():
                     # Renomear para remover prefixo se necessário ou usar nome direto
                     nome_planilha = f"Detalhe_{nome_aba}"
                     if not df_detalhe.empty:
                         # Usar _criar_df_lista_processos apenas para garantir colunas, se necessário
                         df_formatado = self._criar_df_lista_processos(df_detalhe)
                         df_formatado.to_excel(writer, sheet_name=nome_planilha, index=False)
                         self.logger.info("Abas de Detalhe por Indicador criadas.")

            self.logger.info("Relatório Excel gerado no buffer com sucesso."); return True
        except Exception as e:
            self.logger.error(f"ERRO ao gerar/salvar relatório no buffer: {e}")
            self.logger.error(traceback.format_exc())
            st.error(f"Erro ao escrever o arquivo Excel: {e}")
            return False

# ============================================================
# Funções de Geração de Gráficos Plotly (Snapshot) - Reutilizadas
# ============================================================
# (Cole aqui as funções gerar_grafico_... definidas na resposta anterior)
# Exemplo:
def gerar_grafico_status_metas(resultados_metas):
    # (Implementação do código anterior)
    try:
        df_sumario = pd.DataFrame({
            'Meta': ['Meta 1', 'Meta 2', 'Meta 3'],
            'Base': [resultados_metas['meta1'].get('P1.1', 0), resultados_metas['meta2'].get('P2.1', 0), resultados_metas['meta3'].get('P3.1', 0)],
            'Resolvido/No Prazo': [resultados_metas['meta1'].get('P1.2', 0), resultados_metas['meta2'].get('P2.2', 0), resultados_metas['meta3'].get('P3.2', 0)]
        })
        df_melt = df_sumario.melt(id_vars='Meta', var_name='Indicador', value_name='Quantidade')
        fig = px.bar(df_melt, x='Meta', y='Quantidade', color='Indicador', barmode='group',
                     title="Status das Metas (Base x Realizado)", text_auto=True)
        fig.update_layout(yaxis_title="Quantidade de Processos")
        return fig
    except Exception as e:
         logging.error(f"Erro ao gerar grafico status metas: {e}")
         return go.Figure().update_layout(title="Erro ao gerar Gráfico Status Metas")

def gerar_grafico_prazos_meta3(df_cabecalhos_rel, ids_pendentes_snapshot, data_snapshot):
     # (Implementação do código anterior)
     try:
         if not ids_pendentes_snapshot: return go.Figure().update_layout(title="Sem Pendentes para Meta 3")
         cfg = ConfiguracaoMetas() # Para pegar constantes
         df_pend = df_cabecalhos_rel[df_cabecalhos_rel[cfg.COLUNA_ID_PROCESSO].isin(ids_pendentes_snapshot)][[cfg.COLUNA_ID_PROCESSO, cfg.COLUNA_DATA_AUTUACAO]].copy()
         df_pend[cfg.COLUNA_DATA_AUTUACAO] = pd.to_datetime(df_pend[cfg.COLUNA_DATA_AUTUACAO], errors='coerce') # Garantir datetime
         df_pend = df_pend.dropna(subset=[cfg.COLUNA_DATA_AUTUACAO])

         if df_pend.empty: return go.Figure().update_layout(title="Sem Datas Válidas para Pendentes Meta 3")

         df_pend['Data Limite'] = df_pend[cfg.COLUNA_DATA_AUTUACAO] + timedelta(days=cfg.PRAZO_DIAS_META3)
         df_pend['Dias Restantes'] = (df_pend['Data Limite'] - data_snapshot).dt.days

         fig = px.histogram(df_pend, x="Dias Restantes", nbins=30,
                            title=f"Distribuição de Prazos Pendentes - Meta 3 ({cfg.PRAZO_DIAS_META3} dias)")
         fig.update_layout(xaxis_title="Dias Restantes até o Prazo Limite", yaxis_title="Quantidade de Processos")
         fig.add_vline(x=0, line_width=2, line_dash="dash", line_color="red")
         return fig
     except Exception as e:
         logging.error(f"Erro ao gerar grafico prazos meta3: {e}")
         return go.Figure().update_layout(title="Erro ao gerar Gráfico Prazos Meta 3")


def gerar_grafico_volume_tarefas(df_tarefas_ativas):
    # (Implementação do código anterior)
     try:
         if df_tarefas_ativas is None or df_tarefas_ativas.empty:
             return go.Figure().update_layout(title="Sem Tarefas Ativas para Analisar Volume")

         contagem = df_tarefas_ativas['FLUXO_TAREFA'].value_counts().reset_index()
         contagem.columns = ['FLUXO_TAREFA', 'count']
         contagem = contagem.sort_values('count', ascending=True)

         fig = px.bar(contagem.tail(25),
                      x='count', y='FLUXO_TAREFA', orientation='h',
                      title="Volume de Processos por Tarefa Ativa (Top 25)", text_auto=True)
         fig.update_layout(xaxis_title="Quantidade de Processos Ativos", yaxis_title="Fluxo > Tarefa", height=600) # Aumentar altura
         return fig
     except Exception as e:
         logging.error(f"Erro ao gerar grafico volume tarefas: {e}")
         return go.Figure().update_layout(title="Erro ao gerar Gráfico Volume Tarefas")


def gerar_grafico_duracao_tarefas(df_duracao_historica):
     # (Implementação do código anterior)
     try:
         if df_duracao_historica is None or df_duracao_historica.empty:
             return go.Figure().update_layout(title="Sem Dados Históricos de Duração de Tarefas")

         contagem_tarefas = df_duracao_historica['FLUXO_TAREFA'].value_counts()
         tarefas_comuns = contagem_tarefas[contagem_tarefas >= 5].index
         df_filtrado = df_duracao_historica[df_duracao_historica['FLUXO_TAREFA'].isin(tarefas_comuns)]

         if df_filtrado.empty:
              return go.Figure().update_layout(title="Poucos Dados Históricos por Tarefa para Box Plot")

         fig = px.box(df_filtrado.sort_values('FLUXO_TAREFA'),
                      x='FLUXO_TAREFA', y='DURACAO_DIAS',
                      title="Duração Histórica por Tarefa (Dias)",
                      points=False)
         fig.update_layout(xaxis_title="Fluxo > Tarefa", yaxis_title="Duração da Tarefa (Dias)")
         fig.update_xaxes(tickangle=-45) # Melhor ângulo para box plot
         return fig
     except Exception as e:
         logging.error(f"Erro ao gerar grafico duracao tarefas: {e}")
         return go.Figure().update_layout(title="Erro ao gerar Gráfico Duração Tarefas")


def gerar_grafico_idade_tarefa(df_tarefas_ativas_com_idade):
     # (Implementação do código anterior)
     try:
         if df_tarefas_ativas_com_idade is None or df_tarefas_ativas_com_idade.empty:
             return go.Figure().update_layout(title="Sem Tarefas Ativas para Analisar Idade")

         contagem_idade = df_tarefas_ativas_com_idade.groupby(['FLUXO_TAREFA', 'FAIXA_IDADE_TAREFA'], observed=False).size().reset_index(name='count')

         contagem_total_tarefa = df_tarefas_ativas_com_idade['FLUXO_TAREFA'].value_counts().reset_index()
         contagem_total_tarefa.columns = ['FLUXO_TAREFA', 'total_count']
         top_tarefas = contagem_total_tarefa.head(25)['FLUXO_TAREFA'].tolist()
         contagem_idade_filtrada = contagem_idade[contagem_idade['FLUXO_TAREFA'].isin(top_tarefas)].copy() # Adiciona copy

         if contagem_idade_filtrada.empty:
              return go.Figure().update_layout(title="Sem dados de idade para tarefas Top 25")


         # Assegurar que FAIXA_IDADE_TAREFA é categórica ordenada
         faixas_ordem = ['0-30 dias', '31-90 dias', '91-180 dias', '> 180 dias']
         contagem_idade_filtrada['FAIXA_IDADE_TAREFA'] = pd.Categorical(
             contagem_idade_filtrada['FAIXA_IDADE_TAREFA'],
             categories=faixas_ordem,
             ordered=True
         )
         # Ordenar para o gráfico
         contagem_idade_filtrada = contagem_idade_filtrada.sort_values(['FLUXO_TAREFA', 'FAIXA_IDADE_TAREFA'])


         fig = px.bar(contagem_idade_filtrada,
                      x='count', y='FLUXO_TAREFA', color='FAIXA_IDADE_TAREFA', orientation='h',
                      title="Tempo Parado na Tarefa Atual (Top 25 Tarefas)",
                      category_orders={"FAIXA_IDADE_TAREFA": faixas_ordem},
                      color_discrete_sequence=px.colors.sequential.YlOrRd)
         fig.update_layout(xaxis_title="Quantidade de Processos Ativos", yaxis_title="Fluxo > Tarefa",
                           yaxis={'categoryorder':'total ascending'}, height=600) # Ordena barras e aumenta altura
         return fig
     except Exception as e:
         logging.error(f"Erro ao gerar grafico idade tarefa: {e}")
         return go.Figure().update_layout(title="Erro ao gerar Gráfico Idade na Tarefa")


# ============================================================
# Interface Streamlit Principal
# ============================================================

# --- Estado da Sessão para Armazenar Resultados ---
if 'analise_concluida' not in st.session_state:
    st.session_state.analise_concluida = False
if 'dados_analise' not in st.session_state:
    st.session_state.dados_analise = None
if 'buffer_excel' not in st.session_state:
    st.session_state.buffer_excel = None
if 'data_referencia_analise' not in st.session_state:
     st.session_state.data_referencia_analise = None


# --- Layout Principal ---
st.title("📊 Monitor de Metas e Gargalos - Corregedorias - Por Cristhiano Leite dos Santos")
st.write(f"Análise para o ano base de **{ConfiguracaoMetas.ANO_META}**") # Usa ano da config

# --- Barra Lateral para Controles ---
with st.sidebar:
    st.header("Arquivos de Entrada")
    uploaded_cabecalhos = st.file_uploader("1. Cabeçalhos (.csv, .xlsx)", type=['csv', 'xlsx', 'xls'], key="up_cab")
    uploaded_movimentos = st.file_uploader("2. Movimentos (.csv, .xlsx)", type=['csv', 'xlsx', 'xls'], key="up_mov")
    uploaded_tarefas = st.file_uploader("3. Tarefas (.csv, .xlsx)", type=['csv', 'xlsx', 'xls'], key="up_tar")

    st.header("Data de Referência")
    default_date = datetime.now().date()
    data_referencia = st.date_input("Selecione a data para o 'Snapshot'", value=default_date, key="dt_ref")
    # Converter data para datetime no fim do dia para incluir todos os eventos do dia
    data_referencia_dt = datetime.combine(data_referencia, datetime.max.time())

    st.header("Executar")
    run_button = st.button("▶️ Iniciar Análise", key="btn_run", type="primary")

# --- Lógica Principal de Análise ---
if run_button:
    # Limpar resultados anteriores ao iniciar nova análise
    st.session_state.analise_concluida = False
    st.session_state.dados_analise = None
    st.session_state.buffer_excel = None
    st.session_state.data_referencia_analise = data_referencia # Guarda a data usada

    if uploaded_cabecalhos and uploaded_movimentos and uploaded_tarefas:
        all_files_valid = True
        dados_analise_completa = None
        buffer_excel_gerado = None

        with st.spinner("Carregando e validando dados... Por favor, aguarde."):
            try:
                cfg = ConfiguracaoMetas()
                carregador = CarregadorDados(config=cfg, logger=logging.getLogger("Carregador"))

                # Usar st.session_state para talvez guardar DFs carregados? Por enquanto não.
                df_cabecalhos = carregador.carregar_arquivo(uploaded_cabecalhos, cfg.COLUNAS_ESSENCIAIS_CABECALHO, "Cabeçalhos")
                df_movimentos = carregador.carregar_arquivo(uploaded_movimentos, cfg.COLUNAS_ESSENCIAIS_MOVIMENTOS, "Movimentos")
                df_tarefas = carregador.carregar_arquivo(uploaded_tarefas, cfg.COLUNAS_ESSENCIAIS_TAREFAS, "Tarefas")

                if df_cabecalhos is None or df_movimentos is None or df_tarefas is None:
                    st.error("Falha ao carregar ou validar um ou mais arquivos. Verifique as mensagens acima ou o log.")
                    all_files_valid = False
                else:
                    st.success("Arquivos carregados com sucesso!")

            except Exception as e_load:
                 st.error(f"Erro crítico durante carregamento: {e_load}")
                 logging.error(f"Erro crítico carregamento: {traceback.format_exc()}")
                 all_files_valid = False

        if all_files_valid:
            with st.spinner(f"Executando análise completa para {data_referencia.strftime('%d/%m/%Y')}..."):
                try:
                    analisador = AnalisadorMetas(config=cfg, logger=logging.getLogger("Analisador"))
                    dados_analise_completa = analisador.executar_analise(df_cabecalhos, df_movimentos, df_tarefas, data_referencia_dt)

                    if dados_analise_completa:
                         st.success(f"Análise concluída para {data_referencia.strftime('%d/%m/%Y')}!")
                         st.session_state.dados_analise = dados_analise_completa # Guarda no estado
                         st.session_state.analise_concluida = True

                         # Gerar Excel imediatamente e guardar no estado
                         with st.spinner("Gerando relatório Excel..."):
                              gerador_xls = GeradorRelatorio(config=cfg, logger=logging.getLogger("GeradorExcel"))
                              buffer_excel_gerado = io.BytesIO()
                              sucesso_xls = gerador_xls.salvar_relatorio(dados_analise_completa, buffer_excel_gerado)
                              if sucesso_xls:
                                   st.session_state.buffer_excel = buffer_excel_gerado
                              else:
                                   st.error("Falha ao gerar o buffer do Excel.")
                                   st.session_state.buffer_excel = None

                    else:
                         st.error("A análise falhou ou não retornou resultados.")
                         st.session_state.analise_concluida = False


                except Exception as e_analise:
                    st.error(f"Ocorreu um erro durante a análise: {e_analise}")
                    st.error("Verifique os arquivos de entrada e as configurações. Detalhes no log se executado via terminal.")
                    logging.error(f"Erro crítico análise: {traceback.format_exc()}")
                    st.session_state.analise_concluida = False

    else:
        st.warning("Por favor, carregue os três arquivos necessários na barra lateral esquerda.")
        st.session_state.analise_concluida = False # Resetar se arquivos não estão presentes

# --- Exibição Condicional dos Resultados ---
if st.session_state.analise_concluida and st.session_state.dados_analise:
    st.header(f"Resultados da Análise - Snapshot: {st.session_state.data_referencia_analise.strftime('%d/%m/%Y')}")

    dados_analise = st.session_state.dados_analise
    resultados_metas = dados_analise.get('resultados_metas')
    dfs_detalhes_metas = dados_analise.get('dfs_detalhes_metas')
    resultados_tarefas = dados_analise.get('resultados_tarefas')
    df_cabecalhos_rel = dados_analise.get('df_cabecalhos_rel')
    ids_relevantes = dados_analise.get('ids_relevantes')
    ids_pendentes_snapshot = dfs_detalhes_metas.get('Pendentes_Snapshot', pd.DataFrame())[ConfiguracaoMetas.COLUNA_ID_PROCESSO].tolist()


    # Abas para organizar
    tab_metas, tab_gargalos, tab_download = st.tabs(["🎯 Desempenho Metas", "⏳ Análise de Gargalos", " Fazer Download"])

    with tab_metas:
        st.subheader("Status das Metas")
        if resultados_metas:
            col1, col2, col3 = st.columns(3)
            col1.metric("Meta 1 (% Resolvidos / Distribuídos)", f"{resultados_metas.get('meta1', {}).get('percentual', 0):.2f}%", f"{resultados_metas.get('meta1', {}).get('P1.2', 0)} / {resultados_metas.get('meta1', {}).get('P1.1', 0)}")
            col2.metric("Meta 2 (% Resolvidos / Base Antigos)", f"{resultados_metas.get('meta2', {}).get('percentual', 0):.2f}%", f"{resultados_metas.get('meta2', {}).get('P2.2', 0)} / {resultados_metas.get('meta2', {}).get('P2.1', 0)}")
            col3.metric("Meta 3 Adapt. (% Decid. Prazo / Decid.)", f"{resultados_metas.get('meta3', {}).get('percentual', 0):.2f}%", f"{resultados_metas.get('meta3', {}).get('P3.2', 0)} / {resultados_metas.get('meta3', {}).get('P3.1', 0)}")

            fig_status_metas = gerar_grafico_status_metas(resultados_metas)
            st.plotly_chart(fig_status_metas, use_container_width=True)
        else:
            st.warning("Não foi possível calcular os resultados das metas.")

        st.subheader("Urgência Meta 3")
        if df_cabecalhos_rel is not None and ids_pendentes_snapshot is not None:
             # Passar a data de referência correta
             fig_prazos_m3 = gerar_grafico_prazos_meta3(df_cabecalhos_rel, ids_pendentes_snapshot, data_referencia_dt)
             st.plotly_chart(fig_prazos_m3, use_container_width=True)
        else:
             st.warning("Dados insuficientes para gerar gráfico de prazos da Meta 3.")


    with tab_gargalos:
        st.subheader("Onde Estão os Processos Parados Agora?")
        if resultados_tarefas:
            fig_vol_tarefas = gerar_grafico_volume_tarefas(resultados_tarefas.get('tarefas_ativas'))
            st.plotly_chart(fig_vol_tarefas, use_container_width=True)

            st.subheader("Há Quanto Tempo Estão Parados na Tarefa Atual?")
            fig_idade_tarefa = gerar_grafico_idade_tarefa(resultados_tarefas.get('df_tarefas_ativas_com_idade'))
            st.plotly_chart(fig_idade_tarefa, use_container_width=True)

            st.subheader("Quais Tarefas Historicamente Demoram Mais?")
            fig_dur_tarefas = gerar_grafico_duracao_tarefas(resultados_tarefas.get('duracao_historica'))
            st.plotly_chart(fig_dur_tarefas, use_container_width=True)
        else:
             st.warning("Não foi possível realizar a análise de tarefas/gargalos.")


    with tab_download:
        st.subheader("Download do Relatório Completo")
        buffer_excel = st.session_state.buffer_excel
        if buffer_excel:
            st.download_button(
                label="💾 Baixar Relatório Excel (.xlsx)",
                data=buffer_excel,
                file_name=f"Relatorio_Metas_Gargalos_{st.session_state.data_referencia_analise.strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key='download_excel'
            )
        else:
            st.warning("O relatório Excel não foi gerado ou houve um erro. Tente executar a análise novamente.")

elif run_button:
     # Se o botão foi clicado mas a análise não concluiu com sucesso (já tratado acima)
     # Apenas mostra uma mensagem geral se nenhuma outra foi mostrada
     if not (uploaded_cabecalhos and uploaded_movimentos and uploaded_tarefas):
         pass # Warning já foi mostrado
     else:
         # Algum erro ocorreu durante a análise que não foi pego pelos try/except específicos
         st.error("A análise não pôde ser concluída. Verifique os logs ou tente novamente.")

else:
    st.info("⬅️ Carregue os arquivos de Cabeçalhos, Movimentos e Tarefas na barra lateral, selecione a data e clique em 'Iniciar Análise'.")