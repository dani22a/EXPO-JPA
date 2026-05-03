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

    @GetMapping("/cliente/{clienteId}")
    public Page<CuentaDto> porCliente(@PathVariable Long clienteId, Pageable pageable) {
        return service.listarPorCliente(clienteId, pageable);
    }

    @GetMapping("/cliente/{clienteId}/saldo-total")
    public Map<String, BigDecimal> saldoTotal(@PathVariable Long clienteId) {
        return Map.of("saldoTotal", service.saldoTotalDeCliente(clienteId));
    }

    @GetMapping("/top")
    public List<CuentaDto> top(@RequestParam(defaultValue = "5") int limite) {
        return service.topCuentasRicas(limite);
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public CuentaDto crear(@Valid @RequestBody CrearCuentaRequest req) {
        return service.crear(req);
    }

    @PostMapping("/{id}/movimientos")
    @ResponseStatus(HttpStatus.CREATED)
    public MovimientoDto registrarMovimiento(
        @PathVariable Long id,
        @Valid @RequestBody CrearMovimientoRequest req
    ) {
        return service.registrarMovimiento(id, req);
    }

    public record TransferenciaRequest(Long origenId, Long destinoId, BigDecimal monto) {}

    @PostMapping("/transferir")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    public void transferir(@RequestBody TransferenciaRequest req) {
        service.transferir(req.origenId(), req.destinoId(), req.monto());
    }
}
