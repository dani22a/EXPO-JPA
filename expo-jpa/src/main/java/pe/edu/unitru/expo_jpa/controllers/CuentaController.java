package pe.edu.unitru.expo_jpa.controllers;

import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;
import pe.edu.unitru.expo_jpa.dto.CrearCuentaRequest;
import pe.edu.unitru.expo_jpa.dto.CrearMovimientoRequest;
import pe.edu.unitru.expo_jpa.dto.CuentaDto;
import pe.edu.unitru.expo_jpa.dto.MovimientoDto;
import pe.edu.unitru.expo_jpa.services.CuentaService;

import java.math.BigDecimal;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/cuentas")
@RequiredArgsConstructor
public class CuentaController {

    private final CuentaService service;

    @GetMapping("/{id}")
    public CuentaDto obtener(@PathVariable Long id) {
        return service.obtener(id);
    }

    // Pageable se construye automáticamente desde query params: ?page=0&size=10&sort=saldo,desc
    @GetMapping("/cliente/{clienteId}")
    public Page<CuentaDto> porCliente(@PathVariable Long clienteId, Pageable pageable) {
        return service.listarPorCliente(clienteId, pageable);
    }

    // Devuelve un objeto JSON simple { "saldoTotal": 12345.67 }
    @GetMapping("/cliente/{clienteId}/saldo-total")
    public Map<String, BigDecimal> saldoTotal(@PathVariable Long clienteId) {
        return Map.of("saldoTotal", service.saldoTotalDeCliente(clienteId));
    }

    // @RequestParam: query string. Ej: GET /api/cuentas/top?limite=3
    @GetMapping("/top")
    public List<CuentaDto> top(@RequestParam(defaultValue = "5") int limite) {
        return service.topCuentasRicas(limite);
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public CuentaDto crear(@Valid @RequestBody CrearCuentaRequest req) {
        return service.crear(req);
    }

    // Endpoint anidado: POST /api/cuentas/1/movimientos
    @PostMapping("/{id}/movimientos")
    @ResponseStatus(HttpStatus.CREATED)
    public MovimientoDto registrarMovimiento(
        @PathVariable Long id,
        @Valid @RequestBody CrearMovimientoRequest req
    ) {
        return service.registrarMovimiento(id, req);
    }

    // Record nested: estructura simple del payload de transferencia.
    public record TransferenciaRequest(Long origenId, Long destinoId, BigDecimal monto) {}

    // Operación que toca DOS cuentas en una sola transacción atómica.
    @PostMapping("/transferir")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    public void transferir(@RequestBody TransferenciaRequest req) {
        service.transferir(req.origenId(), req.destinoId(), req.monto());
    }
}
