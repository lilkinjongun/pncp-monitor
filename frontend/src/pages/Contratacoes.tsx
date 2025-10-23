import { useEffect, useState } from "react";
import DashboardLayout from "@/components/DashboardLayout";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ExternalLink, RefreshCw } from "lucide-react";

interface Contratacao {
  id: number;
  numero_compra: string;
  ano_compra: number;
  objeto: string;
  valor_estimado: number;
  modalidade_nome: string;
  data_publicacao: string;
  situacao: string;
  link_pncp: string;
}

export default function Contratacoes() {
  const [contratacoes, setContratacoes] = useState<Contratacao[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    carregarContratacoes();
  }, []);

  const carregarContratacoes = () => {
    setLoading(true);
    // Simular carregamento de dados
    // Em produção, isso viria de uma API
    setTimeout(() => {
      setContratacoes([
        {
          id: 1,
          numero_compra: "00017/2025",
          ano_compra: 2025,
          objeto: "Aquisição de Artefatos de Cimento",
          valor_estimado: 7631669.79,
          modalidade_nome: "Pregão - Eletrônico",
          data_publicacao: "2025-05-12T08:16:48",
          situacao: "Publicada",
          link_pncp: "https://pncp.gov.br/app/editais/29138448000198/2025/17",
        },
        {
          id: 2,
          numero_compra: "00042/2025",
          ano_compra: 2025,
          objeto: "Registro de preços para eventual prestação de serviços para a realização de exames",
          valor_estimado: 242030.00,
          modalidade_nome: "Pregão - Eletrônico",
          data_publicacao: "2025-05-13T07:19:16",
          situacao: "Publicada",
          link_pncp: "https://pncp.gov.br/app/editais/29138448000198/2025/42",
        },
        {
          id: 3,
          numero_compra: "00018/2025",
          ano_compra: 2025,
          objeto: "Eventual prestação de serviço de staff",
          valor_estimado: 720591.72,
          modalidade_nome: "Pregão - Eletrônico",
          data_publicacao: "2025-05-14T07:05:04",
          situacao: "Publicada",
          link_pncp: "https://pncp.gov.br/app/editais/29138448000198/2025/18",
        },
      ]);
      setLoading(false);
    }, 500);
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
    }).format(value);
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
    });
  };

  const getModalidadeBadgeVariant = (modalidade: string) => {
    if (modalidade.includes('Pregão')) return 'default';
    if (modalidade.includes('Dispensa')) return 'secondary';
    if (modalidade.includes('Inexigibilidade')) return 'outline';
    return 'default';
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Contratações</h1>
            <p className="text-muted-foreground mt-2">
              Lista completa de contratações monitoradas
            </p>
          </div>
          <Button onClick={carregarContratacoes} disabled={loading}>
            <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Atualizar
          </Button>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Todas as Contratações</CardTitle>
            <CardDescription>
              {contratacoes.length} contratação(ões) encontrada(s)
            </CardDescription>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="space-y-3">
                {[1, 2, 3].map((i) => (
                  <div key={i} className="h-16 animate-pulse rounded bg-muted" />
                ))}
              </div>
            ) : (
              <div className="rounded-md border">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Número</TableHead>
                      <TableHead>Objeto</TableHead>
                      <TableHead>Modalidade</TableHead>
                      <TableHead>Valor Estimado</TableHead>
                      <TableHead>Data</TableHead>
                      <TableHead className="text-right">Ações</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {contratacoes.length === 0 ? (
                      <TableRow>
                        <TableCell colSpan={6} className="text-center text-muted-foreground py-8">
                          Nenhuma contratação encontrada
                        </TableCell>
                      </TableRow>
                    ) : (
                      contratacoes.map((contratacao) => (
                        <TableRow key={contratacao.id}>
                          <TableCell className="font-medium">
                            {contratacao.numero_compra}
                          </TableCell>
                          <TableCell className="max-w-md">
                            <div className="truncate" title={contratacao.objeto}>
                              {contratacao.objeto}
                            </div>
                          </TableCell>
                          <TableCell>
                            <Badge variant={getModalidadeBadgeVariant(contratacao.modalidade_nome)}>
                              {contratacao.modalidade_nome}
                            </Badge>
                          </TableCell>
                          <TableCell className="font-mono text-sm">
                            {formatCurrency(contratacao.valor_estimado)}
                          </TableCell>
                          <TableCell>
                            {formatDate(contratacao.data_publicacao)}
                          </TableCell>
                          <TableCell className="text-right">
                            <Button
                              variant="ghost"
                              size="sm"
                              asChild
                            >
                              <a
                                href={contratacao.link_pncp}
                                target="_blank"
                                rel="noopener noreferrer"
                              >
                                <ExternalLink className="h-4 w-4 mr-2" />
                                Ver no PNCP
                              </a>
                            </Button>
                          </TableCell>
                        </TableRow>
                      ))
                    )}
                  </TableBody>
                </Table>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
}

